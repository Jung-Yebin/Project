from flask import Flask,redirect,render_template,url_for,request,session,flash
from DB import DBModule
import requests as req

app = Flask(__name__)
app.secret_key = "weggkfk!dfkwwgegvg"
DB = DBModule()

@app.route("/")
def index():
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"
    return render_template("index.html", user = user)

@app.route("/logout")
def logout():
    if "uid" in session:
        session.pop("uid")
        return redirect(url_for("index"))
    return redirect(url_for("login"))

@app.route("/login")
def login():
    if "uid" in session:
        flash("로그인")
        return redirect(url_for("index"))
    else:
        return render_template("login.html")

@app.route("/login_done", methods=["get"])
def login_done():
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    if DB.login(uid, pwd):
        session["uid"] = uid
        return redirect(url_for("index"))
    else:
        flash("로그인에 실패하였습니다")
        return redirect(url_for("login"))

@app.route("/findaccount", methods=['get'])
def find_account():

    name = request.args.get("name")
    number = request.args.get("phone")

    users = DB.find_account()

    name_val = []
    number_val = []
    for k, v in users.items():

        for k2, v2 in v.items():
            if v2 == name:
                name_val.append(k)

        for k3, v3 in v.items():
            if v3 == number:
                number_val.append(k)

    result = []
    for i in set(name_val):
        for j in set(number_val):
            if i == j:
                result.append(i)

    if len(result) != 0:
        key = result.pop()

        user_id = ''
        for k, v in users.items():
            if k == key:
                for id_k, id_v in v.items():
                    if id_k == 'id':
                        user_id = id_v
        user_pwd = ''
        for k, v in users.items():
            if k == key:
                for pwd_k, pwd_v in v.items():
                    if pwd_k == 'pw':
                        user_pwd = pwd_v

        if name == '' or number == '':
            return render_template("findaccount.html")


        return render_template('pop.html', id = user_id, pwd = user_pwd)

    else:
        return render_template("findaccount.html")

@app.route("/user/<string:uid>")
def user_posts(uid):
    u_budget, u_thismonth, u_usage, u_predict,uthisyear = DB.user_detail(uid)
    u_budget = int(u_budget)

    try:
        per = round((u_thismonth / u_budget) * 100)
    except:
        per = 0

    if u_predict == 0:
        u_predict = "해당 기능을 사용하기 위해서는 2개 이상의 제품을 구매하셔야 합니다."

    return render_template("mybudget.html", uid=uid, ubudget = u_budget, uthismonth = u_thismonth, usage=u_usage, predict_usage=u_predict, per=per,uthisyear = uthisyear)

@app.route("/user/mypage/<string:uid>")
def my_page(uid):
    users_id,users_name,users_gender,users_birth,users_number,users_job = DB.users_page(uid)

    return render_template("mypage.html", uid=uid, id = users_id,name=users_name,gender=users_gender,birth=users_birth,number=users_number,job=users_job)

@app.route("/user/star/<string:uid>")
def star(uid):
    gen_freq, gen_cost, job_freq, job_cost, total_freq, total_cost = DB.star(uid)

    if gen_freq == '식비':
        gen_catenum = 1
    elif gen_freq == '금융':
        gen_catenum = 2
    elif gen_freq == '미용&뷰티':
        gen_catenum = 3
    elif gen_freq == '통신':
        gen_catenum = 4
    elif gen_freq == '의류&잡화':
        gen_catenum = 5
    elif gen_freq == '경조사':
        gen_catenum = 6
    elif gen_freq == '취미&여가':
        gen_catenum = 7
    elif gen_freq == '문화':
        gen_catenum = 8
    elif gen_freq == '교육':
        gen_catenum = 9
    elif gen_freq == '주거&생활':
        gen_catenum = 10
    elif gen_freq == '건강':
        gen_catenum = 11
    elif gen_freq == '교통':
        gen_catenum = 12
    elif gen_freq == '문구&디지털':
        gen_catenum = 13
    elif gen_freq == '기타':
        gen_catenum = 14
    else :
        gen_catenum = 0

    if job_freq == '식비':
        job_catenum = 1
    elif job_freq == '금융':
        job_catenum = 2
    elif job_freq == '미용&뷰티':
        job_catenum = 3
    elif job_freq == '통신':
        job_catenum = 4
    elif job_freq == '의류&잡화':
        job_catenum = 5
    elif job_freq == '경조사':
        job_catenum = 6
    elif job_freq == '취미&여가':
        job_catenum = 7
    elif job_freq == '문화':
        job_catenum = 8
    elif job_freq == '교육':
        job_catenum = 9
    elif job_freq == '주거&생활':
        job_catenum = 10
    elif job_freq == '건강':
        job_catenum = 11
    elif job_freq == '교통':
        job_catenum = 12
    elif job_freq == '문구&디지털':
        job_catenum = 13
    elif job_freq == '기타':
        job_catenum = 14
    else :
        job_catenum = 0
    if total_freq == '식비':
        total_catenum = 1
    elif total_freq == '금융':
        total_catenum = 2
    elif total_freq == '미용&뷰티':
        total_catenum = 3
    elif total_freq == '통신':
        total_catenum = 4
    elif total_freq == '의류&잡화':
        total_catenum = 5
    elif total_freq == '경조사':
        total_catenum = 6
    elif total_freq == '취미&여가':
        total_catenum = 7
    elif total_freq == '문화':
        total_catenum = 8
    elif total_freq == '교육':
        total_catenum = 9
    elif total_freq == '주거&생활':
        total_catenum = 10
    elif total_freq == '건강':
        total_catenum = 11
    elif total_freq == '교통':
        total_catenum = 12
    elif total_freq == '문구&디지털':
        total_catenum = 13
    elif total_freq == '기타':
        total_catenum = 14
    else :
        total_catenum = 0

    return render_template("star.html", uid=uid, genfreq=gen_freq, gencost=gen_cost, jobfreq=job_freq, jobcost = job_cost, totalfreq=total_freq, totalcost=total_cost, gen_catenum = gen_catenum, job_catenum = job_catenum, total_catenum = total_catenum)

@app.route("/user/habit/<string:uid>")
def habit(uid):
    lastmonth,cate,users_budget,users_lastmonth_freq, users_average_consum, u_lastmonth_freq, u_average_consum, u_thismonth_freq, u_thisconsum_sum,ucategory, u_asso_category, users_asso_category = DB.habit(uid)

    users_average_consum = int(users_average_consum)
    users_budget = int(users_budget)

    if len(lastmonth) == 0:
        del lastmonth
        lastmonth = "저번달 소비내역 없음"

    if len(cate) == 0:
        del cate
        cate = "저번달 소비내역 없음"


    if users_lastmonth_freq == 0 or users_average_consum == 0 or u_lastmonth_freq == 0 or u_average_consum == 0 or users_budget == 0:
        length = 0
        message = "정보없음"
        message_num = 0
        consum_type = "정보없음"
    else:
        length = 1

    if u_lastmonth_freq != 0 and users_lastmonth_freq != 0 and u_average_consum != 0 and users_average_consum != 0 and users_budget != 0:
        if u_thismonth_freq <= u_lastmonth_freq and u_thisconsum_sum <= users_budget :
            message = "소비를 잘 하고 있군요!"
            consum_type = "절약형"
            message_num = 1
        if u_thismonth_freq > u_lastmonth_freq and u_thisconsum_sum <= users_budget :
            message = "소비를 잘 하고 있군요 !"
            consum_type = "합리적소비형"
            message_num = 2
        if u_thismonth_freq > u_lastmonth_freq and u_thisconsum_sum <= users_budget:
            message = "조심하세요! 조금 있으면 예산을 넘을 것 같아요!"
            consum_type = "열린지갑형"
            message_num = 3
        if u_thismonth_freq <= u_lastmonth_freq and u_thisconsum_sum > users_budget:
            message = "당신은 카드를 자주 꺼내는군요! 충동구매그만!"
            consum_type = "플렉스형"
            message_num = 4
        if u_thismonth_freq > u_lastmonth_freq and u_thisconsum_sum > users_budget:
            message = "당신은 카드를 자주 꺼내는군요! 충동구매그만!"
            consum_type = "소비중독형"
            message_num = 5

    if ucategory == '식비':
        catenum = 1
    elif ucategory == '금융':
        catenum = 2
    elif ucategory == '미용&뷰티':
        catenum = 3
    elif ucategory == '통신':
        catenum = 4
    elif ucategory == '의류&잡화':
        catenum = 5
    elif ucategory == '경조사':
        catenum = 6
    elif ucategory == '취미&여가':
        catenum = 7
    elif ucategory == '문화':
        catenum = 8
    elif ucategory == '교육':
        catenum = 9
    elif ucategory == '주거&생활':
        catenum = 10
    elif ucategory == '건강':
        catenum = 11
    elif ucategory == '교통':
        catenum = 12
    elif ucategory == '문구&디지털':
        catenum = 13
    elif ucategory == '기타':
        catenum = 14
    else:
        catenum = 0

    if u_asso_category[0] == '식비':
        associationnum = 1
    elif u_asso_category[0] == '금융':
        associationnum = 2
    elif u_asso_category[0] == '미용&뷰티':
        associationnum = 3
    elif u_asso_category[0] == '통신':
        associationnum = 4
    elif u_asso_category[0] == '의류&잡화':
        associationnum = 5
    elif u_asso_category[0] == '경조사':
        associationnum = 6
    elif u_asso_category[0] == '취미&여가':
        associationnum = 7
    elif u_asso_category[0] == '문화':
        associationnum = 8
    elif u_asso_category[0] == '교육':
        associationnum = 9
    elif u_asso_category[0] == '주거&생활':
        associationnum = 10
    elif u_asso_category[0] == '건강':
        associationnum = 11
    elif u_asso_category[0] == '교통':
        associationnum = 12
    elif u_asso_category[0] == '문구&디지털':
        associationnum = 13
    elif u_asso_category[0] == '기타':
        associationnum = 14
    else:
        associationnum = 0
    if users_asso_category[0] == '식비':
        users_associationnum = 1
    elif users_asso_category[0] == '금융':
        users_associationnum = 2
    elif users_asso_category[0] == '미용&뷰티':
        users_associationnum = 3
    elif users_asso_category[0] == '통신':
        users_associationnum = 4
    elif users_asso_category[0] == '의류&잡화':
        users_associationnum = 5
    elif users_asso_category[0] == '경조사':
        users_associationnum = 6
    elif users_asso_category[0] == '취미&여가':
        users_associationnum = 7
    elif users_asso_category[0] == '문화':
        users_associationnum = 8
    elif users_asso_category[0] == '교육':
        users_associationnum = 9
    elif users_asso_category[0] == '주거&생활':
        users_associationnum = 10
    elif users_asso_category[0] == '건강':
        users_associationnum = 11
    elif users_asso_category[0] == '교통':
        users_associationnum = 12
    elif users_asso_category[0] == '문구&디지털':
        users_associationnum = 13
    elif users_asso_category[0] == '기타':
        users_associationnum = 14
    else:
        users_associationnum = 0



    return render_template("habit.html", lastmonth = lastmonth, cate = cate, users_budget = users_budget, message = message, consum_type = consum_type, length = length, message_num = message_num,ucategory = ucategory, u_asso_category = u_asso_category, catenum = catenum, associationnum = associationnum,users_asso_category=users_asso_category, users_associationnum=users_associationnum)

@app.route("/user/category_analysis/<string:uid>")
def category_analysis(uid):
    thismonth_food, thismonth_bank, thismonth_beauty, thismonth_digital, thismonth_communication, thismonth_congratulate, thismonth_leisure, thismonth_culture, thismonth_education, thismonth_live, thismonth_health, thismonth_traffic, thismonth_cloth, thismonth_etc, lastmonth_food, lastmonth_bank, lastmonth_beauty, lastmonth_digital, lastmonth_communication, lastmonth_congratulate, lastmonth_leisure, lastmonth_culture, lastmonth_education, lastmonth_live, lastmonth_health, lastmonth_traffic, lastmonth_cloth, lastmonth_etc, lastmonth_food_rate, lastmonth_bank_rate, lastmonth_beauty_rate, lastmonth_digital_rate, lastmonth_communication_rate, lastmonth_congratulate_rate, lastmonth_leisure_rate, lastmonth_culture_rate, lastmonth_education_rate, lastmonth_live_rate, lastmonth_health_rate, lastmonth_traffic_rate, lastmonth_cloth_rate, lastmonth_etc_rate, twomonth_food, twomonth_bank, twomonth_beauty, twomonth_digital, twomonth_communication, twomonth_congratulate, twomonth_leisure, twomonth_culture, twomonth_education, twomonth_live, twomonth_health, twomonth_traffic, twomonth_cloth, twomonth_etc, threemonth_food, threemonth_bank, threemonth_beauty, threemonth_digital, threemonth_communication, threemonth_congratulate, threemonth_leisure, threemonth_culture, threemonth_education, threemonth_live, threemonth_health, threemonth_traffic, threemonth_cloth, threemonth_etc, fourmonth_food, fourmonth_bank, fourmonth_beauty, fourmonth_digital, fourmonth_communication, fourmonth_congratulate, fourmonth_leisure, fourmonth_culture, fourmonth_education, fourmonth_live, fourmonth_health, fourmonth_traffic, fourmonth_cloth, fourmonth_etc, fivemonth_food, fivemonth_bank, fivemonth_beauty, fivemonth_digital, fivemonth_communication, fivemonth_congratulate, fivemonth_leisure, fivemonth_culture, fivemonth_education, fivemonth_live, fivemonth_health, fivemonth_traffic, fivemonth_cloth, fivemonth_etc, twomonth_food_rate, twomonth_bank_rate, twomonth_beauty_rate, twomonth_digital_rate, twomonth_communication_rate, twomonth_congratulate_rate, twomonth_leisure_rate, twomonth_culture_rate, twomonth_education_rate, twomonth_live_rate, twomonth_health_rate, twomonth_traffic_rate, twomonth_cloth_rate, twomonth_etc_rate, threemonth_food_rate, threemonth_bank_rate, threemonth_beauty_rate, threemonth_digital_rate, threemonth_communication_rate, threemonth_congratulate_rate, threemonth_leisure_rate, threemonth_culture_rate, threemonth_education_rate, threemonth_live_rate, threemonth_health_rate, threemonth_traffic_rate, threemonth_cloth_rate, threemonth_etc_rate, fourmonth_food_rate, fourmonth_bank_rate, fourmonth_beauty_rate, fourmonth_digital_rate, fourmonth_communication_rate, fourmonth_congratulate_rate, fourmonth_leisure_rate, fourmonth_culture_rate, fourmonth_education_rate, fourmonth_live_rate, fourmonth_health_rate, fourmonth_traffic_rate, fourmonth_cloth_rate, fourmonth_etc_rate, fivemonth_food_rate, fivemonth_bank_rate, fivemonth_beauty_rate, fivemonth_digital_rate, fivemonth_communication_rate, fivemonth_congratulate_rate, fivemonth_leisure_rate, fivemonth_culture_rate, fivemonth_education_rate, fivemonth_live_rate, fivemonth_health_rate, fivemonth_traffic_rate, fivemonth_cloth_rate, fivemonth_etc_rate = DB.category_analysis(uid)

    return render_template("category_1.html", thismonth_food=thismonth_food, thismonth_bank=thismonth_bank,
                           thismonth_beauty=thismonth_beauty, thismonth_digital=thismonth_digital,
                           thismonth_communication=thismonth_communication,
                           thismonth_congratulate=thismonth_congratulate, thismonth_leisure=thismonth_leisure,
                           thismonth_culture=thismonth_culture, thismonth_education=thismonth_education,
                           thismonth_live=thismonth_live, thismonth_health=thismonth_health,
                           thismonth_traffic=thismonth_traffic, thismonth_cloth=thismonth_cloth,
                           thismonth_etc=thismonth_etc, lastmonth_food=lastmonth_food, lastmonth_bank=lastmonth_bank,
                           lastmonth_beauty=lastmonth_beauty, lastmonth_digital=lastmonth_digital,
                           lastmonth_communication=lastmonth_communication,
                           lastmonth_congratulate=lastmonth_congratulate, lastmonth_leisure=lastmonth_leisure,
                           lastmonth_culture=lastmonth_culture, lastmonth_education=lastmonth_education,
                           lastmonth_live=lastmonth_live, lastmonth_health=lastmonth_health,
                           lastmonth_traffic=lastmonth_traffic, lastmonth_cloth=lastmonth_cloth,
                           lastmonth_etc=lastmonth_etc, lastmonth_food_rate=lastmonth_food_rate,
                           lastmonth_bank_rate=lastmonth_bank_rate, lastmonth_beauty_rate=lastmonth_beauty_rate,
                           lastmonth_digital_rate=lastmonth_digital_rate,
                           lastmonth_communication_rate=lastmonth_communication_rate,
                           lastmonth_congratulate_rate=lastmonth_congratulate_rate,
                           lastmonth_leisure_rate=lastmonth_leisure_rate, lastmonth_culture_rate=lastmonth_culture_rate,
                           lastmonth_education_rate=lastmonth_education_rate, lastmonth_live_rate=lastmonth_live_rate,
                           lastmonth_health_rate=lastmonth_health_rate, lastmonth_traffic_rate=lastmonth_traffic_rate,
                           lastmonth_cloth_rate=lastmonth_cloth_rate, lastmonth_etc_rate=lastmonth_etc_rate,
                           twomonth_food=twomonth_food, twomonth_bank=twomonth_bank, twomonth_beauty=twomonth_beauty,
                           twomonth_digital=twomonth_digital, twomonth_communication=twomonth_communication,
                           twomonth_congratulate=twomonth_congratulate, twomonth_leisure=twomonth_leisure,
                           twomonth_culture=twomonth_culture, twomonth_education=twomonth_education,
                           twomonth_live=twomonth_live, twomonth_health=twomonth_health,
                           twomonth_traffic=twomonth_traffic, twomonth_cloth=twomonth_cloth, twomonth_etc=twomonth_etc,
                           threemonth_food=threemonth_food, threemonth_bank=threemonth_bank,
                           threemonth_beauty=threemonth_beauty, threemonth_digital=threemonth_digital,
                           threemonth_communication=threemonth_communication,
                           threemonth_congratulate=threemonth_congratulate, threemonth_leisure=threemonth_leisure,
                           threemonth_culture=threemonth_culture, threemonth_education=threemonth_education,
                           threemonth_live=threemonth_live, threemonth_health=threemonth_health,
                           threemonth_traffic=threemonth_traffic, threemonth_cloth=threemonth_cloth,
                           threemonth_etc=threemonth_etc, fourmonth_food=fourmonth_food, fourmonth_bank=fourmonth_bank,
                           fourmonth_beauty=fourmonth_beauty, fourmonth_digital=fourmonth_digital,
                           fourmonth_communication=fourmonth_communication,
                           fourmonth_congratulate=fourmonth_congratulate, fourmonth_leisure=fourmonth_leisure,
                           fourmonth_culture=fourmonth_culture, fourmonth_education=fourmonth_education,
                           fourmonth_live=fourmonth_live, fourmonth_health=fourmonth_health,
                           fourmonth_traffic=fourmonth_traffic, fourmonth_cloth=fourmonth_cloth,
                           fourmonth_etc=fourmonth_etc, fivemonth_food=fivemonth_food, fivemonth_bank=fivemonth_bank,
                           fivemonth_beauty=fivemonth_beauty, fivemonth_digital=fivemonth_digital,
                           fivemonth_communication=fivemonth_communication,
                           fivemonth_congratulate=fivemonth_congratulate, fivemonth_leisure=fivemonth_leisure,
                           fivemonth_culture=fivemonth_culture, fivemonth_education=fivemonth_education,
                           fivemonth_live=fivemonth_live, fivemonth_health=fivemonth_health,
                           fivemonth_traffic=fivemonth_traffic, fivemonth_cloth=fivemonth_cloth,
                           fivemonth_etc=fivemonth_etc,twomonth_food_rate=twomonth_food_rate, twomonth_bank_rate=twomonth_bank_rate, twomonth_beauty_rate = twomonth_beauty_rate, twomonth_digital_rate = twomonth_digital_rate, twomonth_communication_rate = twomonth_communication_rate, twomonth_congratulate_rate=twomonth_congratulate_rate, twomonth_leisure_rate=twomonth_leisure_rate, twomonth_culture_rate=twomonth_culture_rate, twomonth_education_rate=twomonth_education_rate, twomonth_live_rate=twomonth_live_rate, twomonth_health_rate=twomonth_health_rate, twomonth_traffic_rate=twomonth_traffic_rate, twomonth_cloth_rate=twomonth_cloth_rate, twomonth_etc_rate=twomonth_etc_rate, threemonth_food_rate=threemonth_food_rate, threemonth_bank_rate=threemonth_bank_rate, threemonth_beauty_rate=threemonth_beauty_rate, threemonth_digital_rate=threemonth_digital_rate, threemonth_communication_rate=threemonth_communication_rate, threemonth_congratulate_rate=threemonth_congratulate_rate, threemonth_leisure_rate=threemonth_leisure_rate, threemonth_culture_rate=threemonth_culture_rate, threemonth_education_rate=threemonth_education_rate, threemonth_live_rate=threemonth_live_rate, threemonth_health_rate=threemonth_health_rate, threemonth_traffic_rate=threemonth_traffic_rate, threemonth_cloth_rate=threemonth_cloth_rate, threemonth_etc_rate=threemonth_etc_rate, fourmonth_food_rate=fourmonth_food_rate, fourmonth_bank_rate=fourmonth_bank_rate, fourmonth_beauty_rate=fourmonth_beauty_rate, fourmonth_digital_rate=fourmonth_digital_rate, fourmonth_communication_rate=fourmonth_communication_rate, fourmonth_congratulate_rate=fourmonth_congratulate_rate, fourmonth_leisure_rate=fourmonth_leisure_rate, fourmonth_culture_rate=fourmonth_culture_rate, fourmonth_education_rate=fourmonth_education_rate, fourmonth_live_rate=fourmonth_live_rate, fourmonth_health_rate=fourmonth_health_rate, fourmonth_traffic_rate=fourmonth_traffic_rate, fourmonth_cloth_rate=fourmonth_cloth_rate, fourmonth_etc_rate=fourmonth_etc_rate, fivemonth_food_rate=fivemonth_food_rate, fivemonth_bank_rate=fivemonth_bank_rate, fivemonth_beauty_rate=fivemonth_beauty_rate, fivemonth_digital_rate=fivemonth_digital_rate, fivemonth_communication_rate=fivemonth_communication_rate, fivemonth_congratulate_rate=fivemonth_congratulate_rate, fivemonth_leisure_rate=fivemonth_leisure_rate, fivemonth_culture_rate=fivemonth_culture_rate, fivemonth_education_rate=fivemonth_education_rate, fivemonth_live_rate=fivemonth_live_rate, fivemonth_health_rate=fivemonth_health_rate, fivemonth_traffic_rate=fivemonth_traffic_rate, fivemonth_cloth_rate=fivemonth_cloth_rate, fivemonth_etc_rate=fivemonth_etc_rate )

@app.route("/user/category_analysis2/<string:uid>")
def category_analysis2(uid):
    thismonth_food, thismonth_bank, thismonth_beauty, thismonth_digital, thismonth_communication, thismonth_congratulate, thismonth_leisure, thismonth_culture, thismonth_education, thismonth_live, thismonth_health, thismonth_traffic, thismonth_cloth, thismonth_etc, lastmonth_food, lastmonth_bank, lastmonth_beauty, lastmonth_digital, lastmonth_communication, lastmonth_congratulate, lastmonth_leisure, lastmonth_culture, lastmonth_education, lastmonth_live, lastmonth_health, lastmonth_traffic, lastmonth_cloth, lastmonth_etc, lastmonth_food_rate, lastmonth_bank_rate, lastmonth_beauty_rate, lastmonth_digital_rate, lastmonth_communication_rate, lastmonth_congratulate_rate, lastmonth_leisure_rate, lastmonth_culture_rate, lastmonth_education_rate, lastmonth_live_rate, lastmonth_health_rate, lastmonth_traffic_rate, lastmonth_cloth_rate, lastmonth_etc_rate, twomonth_food, twomonth_bank, twomonth_beauty, twomonth_digital, twomonth_communication, twomonth_congratulate, twomonth_leisure, twomonth_culture, twomonth_education, twomonth_live, twomonth_health, twomonth_traffic, twomonth_cloth, twomonth_etc, threemonth_food, threemonth_bank, threemonth_beauty, threemonth_digital, threemonth_communication, threemonth_congratulate, threemonth_leisure, threemonth_culture, threemonth_education, threemonth_live, threemonth_health, threemonth_traffic, threemonth_cloth, threemonth_etc, fourmonth_food, fourmonth_bank, fourmonth_beauty, fourmonth_digital, fourmonth_communication, fourmonth_congratulate, fourmonth_leisure, fourmonth_culture, fourmonth_education, fourmonth_live, fourmonth_health, fourmonth_traffic, fourmonth_cloth, fourmonth_etc, fivemonth_food, fivemonth_bank, fivemonth_beauty, fivemonth_digital, fivemonth_communication, fivemonth_congratulate, fivemonth_leisure, fivemonth_culture, fivemonth_education, fivemonth_live, fivemonth_health, fivemonth_traffic, fivemonth_cloth, fivemonth_etc,twomonth_food_rate, twomonth_bank_rate, twomonth_beauty_rate, twomonth_digital_rate, twomonth_communication_rate, twomonth_congratulate_rate,twomonth_leisure_rate,twomonth_culture_rate,twomonth_education_rate,twomonth_live_rate,twomonth_health_rate,twomonth_traffic_rate,twomonth_cloth_rate,twomonth_etc_rate, = DB.category_analysis(uid)

    return render_template("category_2.html", thismonth_food=thismonth_food, thismonth_bank=thismonth_bank,
                           thismonth_beauty=thismonth_beauty, thismonth_digital=thismonth_digital,
                           thismonth_communication=thismonth_communication,
                           thismonth_congratulate=thismonth_congratulate, thismonth_leisure=thismonth_leisure,
                           thismonth_culture=thismonth_culture, thismonth_education=thismonth_education,
                           thismonth_live=thismonth_live, thismonth_health=thismonth_health,
                           thismonth_traffic=thismonth_traffic, thismonth_cloth=thismonth_cloth,
                           thismonth_etc=thismonth_etc, lastmonth_food=lastmonth_food, lastmonth_bank=lastmonth_bank,
                           lastmonth_beauty=lastmonth_beauty, lastmonth_digital=lastmonth_digital,
                           lastmonth_communication=lastmonth_communication,
                           lastmonth_congratulate=lastmonth_congratulate, lastmonth_leisure=lastmonth_leisure,
                           lastmonth_culture=lastmonth_culture, lastmonth_education=lastmonth_education,
                           lastmonth_live=lastmonth_live, lastmonth_health=lastmonth_health,
                           lastmonth_traffic=lastmonth_traffic, lastmonth_cloth=lastmonth_cloth,
                           lastmonth_etc=lastmonth_etc, lastmonth_food_rate=lastmonth_food_rate,
                           lastmonth_bank_rate=lastmonth_bank_rate, lastmonth_beauty_rate=lastmonth_beauty_rate,
                           lastmonth_digital_rate=lastmonth_digital_rate,
                           lastmonth_communication_rate=lastmonth_communication_rate,
                           lastmonth_congratulate_rate=lastmonth_congratulate_rate,
                           lastmonth_leisure_rate=lastmonth_leisure_rate, lastmonth_culture_rate=lastmonth_culture_rate,
                           lastmonth_education_rate=lastmonth_education_rate, lastmonth_live_rate=lastmonth_live_rate,
                           lastmonth_health_rate=lastmonth_health_rate, lastmonth_traffic_rate=lastmonth_traffic_rate,
                           lastmonth_cloth_rate=lastmonth_cloth_rate, lastmonth_etc_rate=lastmonth_etc_rate,
                           twomonth_food=twomonth_food, twomonth_bank=twomonth_bank, twomonth_beauty=twomonth_beauty,
                           twomonth_digital=twomonth_digital, twomonth_communication=twomonth_communication,
                           twomonth_congratulate=twomonth_congratulate, twomonth_leisure=twomonth_leisure,
                           twomonth_culture=twomonth_culture, twomonth_education=twomonth_education,
                           twomonth_live=twomonth_live, twomonth_health=twomonth_health,
                           twomonth_traffic=twomonth_traffic, twomonth_cloth=twomonth_cloth, twomonth_etc=twomonth_etc,
                           threemonth_food=threemonth_food, threemonth_bank=threemonth_bank,
                           threemonth_beauty=threemonth_beauty, threemonth_digital=threemonth_digital,
                           threemonth_communication=threemonth_communication,
                           threemonth_congratulate=threemonth_congratulate, threemonth_leisure=threemonth_leisure,
                           threemonth_culture=threemonth_culture, threemonth_education=threemonth_education,
                           threemonth_live=threemonth_live, threemonth_health=threemonth_health,
                           threemonth_traffic=threemonth_traffic, threemonth_cloth=threemonth_cloth,
                           threemonth_etc=threemonth_etc, fourmonth_food=fourmonth_food, fourmonth_bank=fourmonth_bank,
                           fourmonth_beauty=fourmonth_beauty, fourmonth_digital=fourmonth_digital,
                           fourmonth_communication=fourmonth_communication,
                           fourmonth_congratulate=fourmonth_congratulate, fourmonth_leisure=fourmonth_leisure,
                           fourmonth_culture=fourmonth_culture, fourmonth_education=fourmonth_education,
                           fourmonth_live=fourmonth_live, fourmonth_health=fourmonth_health,
                           fourmonth_traffic=fourmonth_traffic, fourmonth_cloth=fourmonth_cloth,
                           fourmonth_etc=fourmonth_etc, fivemonth_food=fivemonth_food, fivemonth_bank=fivemonth_bank,
                           fivemonth_beauty=fivemonth_beauty, fivemonth_digital=fivemonth_digital,
                           fivemonth_communication=fivemonth_communication,
                           fivemonth_congratulate=fivemonth_congratulate, fivemonth_leisure=fivemonth_leisure,
                           fivemonth_culture=fivemonth_culture, fivemonth_education=fivemonth_education,
                           fivemonth_live=fivemonth_live, fivemonth_health=fivemonth_health,
                           fivemonth_traffic=fivemonth_traffic, fivemonth_cloth=fivemonth_cloth,
                           fivemonth_etc=fivemonth_etc)

if __name__ == "__main__":
    app.run(host='0.0.0.0')