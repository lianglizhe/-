# @Time : 2020/12/14 20:17


from . import api
from lghome.utils.commons import login_required
from flask import g, request, jsonify, session
from lghome.response_code import RET
from lghome.libs.image_storage import storage
import logging
from lghome.models import User, Area, House, Facility, HouseImage, Order
from lghome import db, constants, redis_store
from lghome import constants
import json
from datetime import datetime


@api.route("/areas")
def get_area_info():

    #用redis中读取数据
    try:
        response_json = redis_store.get("area_info")
    except Exception as e:
        logging.error(e)
    else:
        # redis有缓存数据
        if response_json is not None:
            response_json = json.loads(response_json)
            # print(response_json)
            logging.info('redis cache')
            #return response_json, 200, {"Content-Type": "application/json"}
            return jsonify(errno=RET.OK, errmsg='OK', data=response_json['data'])


    #查询数据库，读取城区信息
    try:
        area_li = Area.query.all()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    area_dict_li = []
    #
    for area in area_li:
        area_dict_li.append(area.to_dict())

    #将数据转成json字符串
    #response_dict = dict(errno=RET.OK, errmsg="ok", data=area_dict_li)
    response_dict = dict(data=area_dict_li)
    response_json = json.dumps(response_dict)

    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, response_json)
    except Exception as e:
        logging.error(e)

    #return response_json, 200, {"Content-Type": "application/json"}
    return jsonify(errno=RET.OK, errmsg="ok", data=area_dict_li)

@api.route("/house/info", methods=["POST"])
@login_required
def save_house_info():
    """ 保存房屋的基本信息   return: 保存失败或者成功
    {
    "title":"1",
    "price":"1",
    "area_id":"8",
    "address":"1",
    "room_count":"1",
    "acreage":"1",
    "unit":"1",
    "capacity":"1",
    "beds":"1",
    "deposit":"1",
    "min_days":"1",
    "max_days":"1",
    "facility":["2","4"]---需要特殊处理
    }"""
    #发布房源用户
    user_id = g.user_id
    #接收参数
    house_data = request.get_json()
    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数 2
    max_days = house_data.get("max_days")  # 最大入住天数 1
    # facility = house_data.get("facility")  # 设备信息

    #校验参数
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    #价格判断
    try:
        price = int(float(price)*100)   #分
        deposit = int(float(deposit)*100)    #分

    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    #判断区域ID
    try:
        area = Area.query.get(area_id)

    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='数据库异常')

    if area is None:
        return jsonify(errno=RET.PARAMERR, errmsg='城区信息有误')



    #保存房屋信息
        # 保存房屋信息
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )
    # 设施信息
    facility_ids = house_data.get("facility")
    if facility_ids:
        try:
            facilitys = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

        if facilitys:
            #表示合法的设备
            house.facilities = facilitys

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")


    #返回结果
    return jsonify(errno=RET.OK, errmsg="ok", data={"house_id":house.id})


#上传房子的图片
@api.route("/house/image", methods=["POST"])
@login_required
def save_house_image():
    """
    保存房屋的图片
    :param:   house_id  房屋的ID   house_image  房屋的图片
    :return:   image_url  房屋图片地址
    """
    #接收参数
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    #校验参数
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    #图片上传到七牛云
    image_data = image_file.read()

    try:
        filename = storage(image_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="图片保存失败")

    #保存图片名字到数据库
    house_image = HouseImage(house_id=house_id, url=filename)
    db.session.add(house_image)

    #处理房屋的主图
    if not house.index_image_url:
        house.index_image_url = filename
        db.session.add(house)


    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")


    image_url = constants.QINIU_URL_DOMAIN + filename
    return jsonify(errno=RET.OK, errmsg='ok', data={"image_url":image_url})

@api.route("/user/houses",methods=["GET"])
@login_required
def get_user_house():
    """
    :return:发布的房源信息
    """
    #获取当前用户
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    #转成字典存放到列表中
    houses_list = []
    if houses:
        for houses in houses:
            houses_list.append(houses.to_basic_dict)    #to_basic_dict 将信息放到字典数据里面

    return jsonify(error=RET.OK, errmsg="ok", data={"houses":houses_list})

@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """ 获取首页房屋信息
    :return:排序后的房屋信息
    """
    #先查询缓存数据
    try:
        result = redis_store.get("home_page_data")
    except Exception as e:
        logging.error(e)
        result = None

    if result:
        return result.decode(), 200, {"Content-Type":"application/json"}
    else:
        try:
    #查询数据库，房屋订单最多的条数
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_NUMS).all()
        except Exception as e:
            return jsonify(error=RET.DBERR, errmsg="查询数据库失败")

        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="查询没有数据")

        houses_list = []
        for house in houses:
            houses_list.append(house.to_basic_dict())

        house_dict = dict(errno=RET.OK, errmsg="okk", data=houses_list)
        json_houses = json.dumps(house_dict)

        try:
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            logging.error(e)

        return json_houses, 200, {"Content-Type": "application/json"}
        #return jsonify(errno=RET.OK, errmsg="ok", data=houses_list)

@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_datail(house_id):
    """
    获取房屋详情   house_id  房屋信息
    :return:
    """
    #当前用户    #g对象中
    user_id = session.get("user_id", "-1")  #取不到值显示-1 （未登录）

    #校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    #先从缓存中查询数据
    try:
        result = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        logging.error(e)
        result = None
    if result:
        return '{"errrno":%s, "errmsg":"ok", data:{"house": %s, "user_id": %s}}'%(RET.OK, result.decode(), user_id), 200, {"Content-Type":"application/json"}


    #查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    house_data = house.to_full_dict()
    #存入redis
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRES, json_house)
    except Exception as e:
        logging.error(e)


    return jsonify(errno=RET.OK, errmsg="okk", data={"house":house_data, "user_id":user_id})


#搜索功能

#aid 区域id
#sd  开始时间
#ed  结束时间
#sk  排序
#p   页码

@api.route("/houses", methods=["GET"])
def get_house_list():
    """房屋搜索页面"""
    #接收参数
    start_date = request.args.get('sd')
    end_date = request.args.get('ed')
    area_id = request.args.get('aid')
    sort_key = request.args.get('sd')
    page = request.args.get('p')

    #校验参数
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")    #字符串转成时间类型
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # if start_date >= end_date:
        #     return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")
        if start_date and end_date:
            assert start_date <= end_date

    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR, errms="日期参数有误")

    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.PARAMERR, errms="区域参数有误")

    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1
    #查询缓存数据
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        logging.error(e)
    else:
        if resp_json:
            return resp_json.decode(), 200, {"Content-Type": "application/json"}


    #校验完成 开始查询数据库
    conflict_orders = None
    #过滤条件
    filter_params = []

    try:
        if start_date and end_date:
            conflict_orders = Order.query.filter(Order.begin_data <= end_date, Order.end_date >=start_date).all()

        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_data <= end_date).all()

    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if conflict_orders:
        #订单中获取冲突的房屋id
        conflict_house_id = [order.house_id for order in conflict_orders]
        if conflict_house_id:
             #house = House.query.filter(House.id.notin_(conflict_house_id))
            filter_params.append(House.id.notin_(conflict_house_id))
    if area_id:
        #查询条件
        filter_params.append(House.area_id == area_id)
    #排序
    if sort_key == "booking":
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc)
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    #处理分页
    page_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_NUMS, error_out=False)
    #总页数
    total_page = page_obj.pages
    #获取数据
    house_li = page_obj.items

    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())
    #
    resp_dict = dict(errno=RET.OK, errmsg="okk", data={"total_page":total_page, "house":houses})
    resp_json = json.dumps(resp_dict)

    #将数据保存到redis中
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    try:
        pipeline = redis_store.pipeline()   #管道
        pipeline.hset(redis_key,page, resp_json)
        pipeline.expire(redis_key, constants.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)
        pipeline.execute()
    except Exception as e:
        logging.error(e)

    return jsonify(errno=RET.OK, errmsg="okk", data={"total_page":total_page, "house":houses})    #data 在前端页面找数据

    #house = House.query.filter(*filter_params)   #*filter_params   *代表的是解包操作

#搜索的数据放到redis中
#house_开始_结束_区域ID_排序_页数
# key value
# house_开始_结束_区域ID_排序 key






















































