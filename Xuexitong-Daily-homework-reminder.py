import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import smtplib
from email.mime.text import MIMEText

email = "3549684852@qq.com"  # 设置全局发件人邮箱


# 邮件
# ------------------------------------------------------------------------------------------------------------------#
def post_email(_receive_email, _content, _title):
    """
    :param _receive_email: 接收方邮箱
    :param _content: 邮件内容
    :param _title: 邮件标题
    """
    mail_host = ''  # 邮箱服务器地址
    mail_user = ''  # 邮箱用户名
    mail_pass = ''  # 邮箱授权码
    sender = email
    receivers = _receive_email
    message = MIMEText(_content, 'plain', 'utf-8')
    message['Subject'] = _title
    message['From'] = sender
    message['To'] = receivers[0]
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)


headers = None


# 登录
# ------------------------------------------------------------------------------------------------------------------#
def login(name, passwd):
    global headers
    headers = {"User-Agent": UserAgent().random}
    while True:
        try:
            # 获取登录cookies
            # ------------------------------------------------------------------------------------------------------------------#
            r = requests.get("https://passport2.chaoxing.com/fanyalogin", headers=headers)
            cookies = dict(r.cookies)
            # ------------------------------------------------------------------------------------------------------------------#
            data = {
                "fid": "-1",
                "uname": name,
                "password": passwd,
                "refer": "https%3A%2F%2Fi.chaoxing.com",
                "t": "true",
                "forbidotherlogin": "0",
                "validate": "",
                "doubleFactorLogin": "0",
                "independentId": "0"
            }
            jsessionid = cookies["JSESSIONID"]
            r = requests.post("https://passport2.chaoxing.com/fanyalogin", headers=headers, data=data, cookies=cookies)
            cookies = dict(**{"JSESSIONID": jsessionid}, **r.cookies)
            # ------------------------------------------------------------------------------------------------------------------#
            r = requests.get("https://i.chaoxing.com/", headers=headers, cookies=cookies, allow_redirects=False)
            # ------------------------------------------------------------------------------------------------------------------#
            cookies = dict(**cookies, **{"source": ""})
            r = requests.get(f"https://i.chaoxing.com/base?t={int(time.time() * 1000)}", headers=headers,
                             cookies=cookies)
            # 获取课程页cookie
            # ------------------------------------------------------------------------------------------------------------------#
            cookies.pop("JSESSIONID")
            cookies = dict(**cookies, **{"spaceFid": "270"}, **{"spaceRoleId": ""})
            r = requests.get("https://mooc1-1.chaoxing.com/visit/interaction", headers=headers, cookies=cookies)
            # ------------------------------------------------------------------------------------------------------------------#
            cookies = dict(**cookies, **r.cookies)
            return cookies
        except:
            continue


# 获取信息
# ------------------------------------------------------------------------------------------------------------------#
def get_work_info(name, password):
    # ------------------------------------------------------------------------------------------------------------------#
    cookies = login(name, password)
    if cookies["_uid"] is None:
        raise
    data = {
        "courseType": "1",
        "courseFolderId": "0",
        "baseEducation": "0",
        "superstarClass": "",
        "courseFolderSize": "0"
    }
    r = requests.post("https://mooc1-1.chaoxing.com/visit/courselistdata", headers=headers, data=data,
                      cookies=cookies)
    soup = BeautifulSoup(r.text, "lxml")
    div_data = soup.find_all("li", class_="course clearfix")
    work_url = []
    for z in div_data:
        if '课程已结束' not in str(z) and '本课程未开课' not in str(z):
            work_url.append(str(z.find("div", class_="course-info").find("a")["href"]).replace("amp;", ""))
    # ------------------------------------------------------------------------------------------------------------------#
    work_info = []
    for z in work_url:
        temp_info = []
        # ------------------------------------------------------------------------------------------------------------------#
        r = requests.get(z, headers=headers, cookies=cookies, allow_redirects=False)
        mas2_url = r.headers["Location"]
        r = requests.get(mas2_url, headers=headers, cookies=cookies)
        if "操作异常" in str(r.text) or "您所浏览的页面不存在" in str(r.text):
            continue
        soup = BeautifulSoup(r.text, "lxml")
        title = str(soup.find("dd", class_="textHidden colorDeep").text).strip()
        work_enc = soup.find("input", id="workEnc")["value"]
        exam_enc = soup.find("input", id="examEnc")["value"]
        open_c = soup.find("input", id="openc")["value"]
        clazzid = soup.find("input", id="clazzid")["value"]
        courseid = soup.find("input", id="courseid")["value"]
        # ------------------------------------------------------------------------------------------------------------------#

        # 查看作业未交情况
        # ------------------------------------------------------------------------------------------------------------------#
        params = mas2_url.replace("courseid", "courseId").replace("clazzid", "classId").split("?")[1].split(
            '&')
        url = "https://mooc1.chaoxing.com/mooc2/work/list?" + "&".join(params[:3]) + "&ut=s&enc=" + work_enc
        r = requests.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(r.text, "lxml")
        li_data = soup.find_all("li")
        for j in li_data:
            if "未交" in str(j) and "time notOver" in str(j) and "tag icon-zy-g" not in str(j):
                temp_info.append(
                    f'--分类: 作业\n--标题: {str(j.find("p", class_="overHidden2 fl").text).strip()}\n--时间: {str(j.find("div", class_="time notOver").text).strip()}')
            elif "未交" in str(j) and "time notOver" not in str(j) and "tag icon-zy-g" not in str(j):
                temp_info.append(
                    f'--分类: 作业\n--标题: {str(j.find("p", class_="overHidden2 fl").text).strip()}\n--时间: 手动结束')
            if "待互评" in str(j) and "time notOver" in str(j) and "tag icon-hp-gy" not in str(j):
                temp_info.append(
                    f'--分类: 互评作业\n--标题: {str(j.find("p", class_="overHidden2 fl").text).strip()}\n--时间: {str(j.find("div", class_="time notOver").text).strip()}')
            elif "待互评" in str(j) and "time notOver" not in str(j) and "tag icon-hp-gy" not in str(j):
                temp_info.append(
                    f'--分类: 互评作业\n--标题: {str(j.find("p", class_="overHidden2 fl").text).strip()}\n--时间:手动结束')
        # ------------------------------------------------------------------------------------------------------------------#

        # 查看考试未交情况
        # ------------------------------------------------------------------------------------------------------------------#
        params = mas2_url.split("?")[1].split('&')
        url = "https://mooc1.chaoxing.com/exam-ans/mooc2/exam/exam-list?" + "&".join(
            params[:3]) + "&ut=s&t=" + str(
            int(time.time() * 1000)) + "&enc=" + exam_enc + "&openc=" + open_c
        r = requests.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(r.text, "lxml")
        li_data = soup.find_all("li")
        for j in li_data:
            if "待做" in str(j) and "time notOver" in str(j) and "tag icon-exam-g" not in str(j):
                temp_info.append(
                    f'--分类: 考试\n--标题: {str(j.find("p", class_="overHidden2 fl").text).strip()}\n--时间: {str(j.find("div", class_="time notOver").text).strip()}')
            elif "待做" in str(j) and "time notOver" not in str(j) and "tag icon-exam-g" not in str(j):
                temp_info.append(
                    f'--分类: 考试\n--标题: {str(j.find("p", class_="overHidden2 fl").text).strip()}\n--时间: 手动结束')
        # ------------------------------------------------------------------------------------------------------------------#

        # 查看任务未交情况
        # ------------------------------------------------------------------------------------------------------------------#
        url = f"https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist?fid=0&courseId={courseid}&classId={clazzid}&showNotStartedActive=0"
        r = requests.get(url, headers=headers, cookies=cookies)
        for j in r.json()["data"]["activeList"]:
            if j["status"] == 1:
                if j["type"] == 35:
                    url = f"https://mobilelearn.chaoxing.com/v2/apis/taskStu/getActiveInfoForMe?fid=0&courseId={courseid}&activeId={j['id']}"
                    r = requests.get(url, headers=headers, cookies=cookies)
                    if r.json()["data"]["toAnswerPage"] == 1:
                        temp_info.append(
                            f'--分类: {str("分组任务").strip()}\n--标题: {str(j["nameOne"]).strip()}\n--时间: {str(j["nameFour"] if j["nameFour"] != "" else "手动结束").strip()}')
                if j["type"] == 14:
                    url = f"https://mobilelearn.chaoxing.com/v2/apis/quiz/quizDetail?activeId={j['id']}"
                    r = requests.get(url, headers=headers, cookies=cookies)
                    if r.json()["data"]["pptUserAttend"] is None:
                        temp_info.append(
                            f'--分类: {str("问卷").strip()}\n--标题: {str(j["nameOne"]).strip()}\n--时间: {str(j["nameFour"] if j["nameFour"] != "" else "手动结束").strip()}')
                if j["type"] == 42:
                    url = f"https://mobilelearn.chaoxing.com/v2/apis/quiz/quizDetail?activeId={j['id']}"
                    r = requests.get(url, headers=headers, cookies=cookies)
                    if r.json()["data"]["pptUserAttend"] is None:
                        temp_info.append(
                            f'--分类: {str("随堂练习").strip()}\n--标题: {str(j["nameOne"]).strip()}\n--时间: {str(j["nameFour"] if j["nameFour"] != "" else "手动结束").strip()}')
                if j["type"] == 23:
                    url = f"https://mobilelearn.chaoxing.com/v2/apis/score/getStuScoreStatus?activeId={j['id']}"
                    r = requests.get(url, headers=headers, cookies=cookies)
                    if r.json()["data"]["userStatus"] == 0:
                        temp_info.append(
                            f'--分类: {str("评分").strip()}\n--标题: {str(j["nameOne"]).strip()}\n--时间: {str(j["nameFour"] if j["nameFour"] != "" else "手动结束").strip()}')
                if j["type"] == 5:
                    url = f"https://mobilelearn.chaoxing.com/v2/apis/discuss/getTopicDiscussInfo?activeId={j['id']}"
                    r = requests.get(url, headers=headers, cookies=cookies)
                    bbsid = r.json()["data"]["bbsid"]
                    uuid = r.json()["data"]["uuid"]
                    url = f"https://groupweb.chaoxing.com/course/topicDiscuss/{bbsid}/{uuid}/getReplyList?order=1&kw=&lastValue=null"
                    r = requests.get(url, headers=headers, cookies=cookies)
                    if len(r.json()["datas"]) < 1:
                        temp_info.append(
                            f'--分类: {str("主题讨论").strip()}\n--标题: {str(j["nameOne"]).strip()}\n--时间: {str(j["nameFour"] if j["nameFour"] != "" else "手动结束").strip()}')
        # ------------------------------------------------------------------------------------------------------------------#
        if len(temp_info) > 0:
            temp_info = title + "\n" + "===============\n" + "\n\n".join(temp_info) + "\n===============\n"
            work_info.append(temp_info)
    return "\n".join(work_info)


# 运行
# ------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    L = [
        ["超星学习通账号", "超星学习通密码", "收件人邮箱", "用户1"],
        ["超星学习通账号", "超星学习通密码", "收件人邮箱", "用户2"],
        ["超星学习通账号", "超星学习通密码", "收件人邮箱", "用户3"],
    ]
    info = []
    content = []
    for i in L:
        try:
            temp = get_work_info(i[0], i[1])
            if len(temp) < 1:
                post_email(i[2],
                           "===============\n暂无作业\n===============",
                           time.strftime('%m月%d日作业提醒'))
                content.append(
                    "===============\n暂无作业\n===============")
                info.append(i[3] + " 发送成功\n")
                continue
            post_email(i[2], temp, time.strftime('%m月%d日作业提醒'))
            content.append(temp)
            info.append(i[3] + " 发送成功\n")
        except:
            content.append("===============\n失败\n===============\n")
            info.append(i[3] + " 发送失败\n")
            continue
    print("\n".join(info))
    post_email(email, "".join(info), "学习通作业推送名单")
    information = []
    for i in range(len(info)):
        information.append(info[i])
        information.append(content[i])
        information.append("\n\n")
    post_email(email, "".join(information), "学习通作业推送详情")
# ------------------------------------------------------------------------------------------------------------------#
