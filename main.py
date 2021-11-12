from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QWidget, QGridLayout, QLabel, \
    QSpacerItem, QSizePolicy, QComboBox, QLineEdit, QPushButton
from pyecharts import Bar, Pie, Line, Overlap
from pyecharts_javascripthon.api import TRANSLATOR
import requests
import json
import datetime as DT


yburl = 'https://api.qweather.com/v7/air/now?' #查找对应城市信息
aurl = 'https://geoapi.qweather.com/v2/city/lookup?' #查找cityid
history_url = 'https://datasetapi.qweather.com/v7/historical/air?'#查找历史天气

value = {
    'location': '北京',
    'key': '102d6f9e820f4db6bf59e89b4c39b276',
    'lang': 'zh',
    'date': '20211022'
}

TITLE_TEXT = "天气情况"  # 主标题
TITLE_SUBTEXT = "过去七天"  # 副标题
index = ["AQI", "pm10", "pm2p5", "no2", "no3", "co", "o3"]
week_ago = ["AQI", "pm10", "pm2p5", "no2", "no3", "co", "o3"]
history = []


class Form(QWidget):
    def __init__(self):
        super(Form, self).__init__()

        self.view = None
        self.echarts = False
        self.initUi()
        self.load_url()

    def initUi(self):
        self.hl = QHBoxLayout(self)
        self.widget = QWidget()
        self.gl = QGridLayout(self.widget)
        #添加查询
        nameLabel = QLabel("城市名称")
        self.nameLineEdit = QLineEdit("")
        self.gl.addWidget(nameLabel, 1 - 1, 0, 1, 1)
        self.gl.addWidget(self.nameLineEdit, 2 - 1, 0, 1, 1)
        save_Btn = QPushButton('查询')
        save_Btn.clicked.connect(self.addNum)
        self.gl.addWidget(save_Btn, 3 - 1, 0, 1, 1)

        # ATTR1
        self.label1 = QLabel(index[0] + ':' + AQI)
        self.label1.setText(index[0] + ':' + AQI)
        self.gl.addWidget(self.label1, 4 - 1, 0, 1, 1)  #向布局中添加内容

        # ATTR2
        self.label2 = QLabel(index[1] + ':' + pm10)
        self.label2.setText(index[1] + ':' + pm10)
        self.gl.addWidget(self.label2, 5 - 1, 0, 1, 1)

        # ATTR3
        self.label3 = QLabel(index[2] + ':' + pm2p5)
        self.label3.setText(index[2] + ':' + pm2p5)
        self.gl.addWidget(self.label3, 6 - 1, 0, 1, 1)

        # ATTR4
        self.label4 = QLabel(index[3] + ':' + no2)
        self.label4.setText(index[3] + ':' + no2)
        self.gl.addWidget(self.label4, 7 - 1, 0, 1, 1)

        # ATTR5
        self.label5 = QLabel(index[4] + ':' + so3)
        self.label5.setText(index[4] + ':' + so3)
        self.gl.addWidget(self.label5, 8 - 1, 0, 1, 1)

        # ATTR6
        self.label6 = QLabel(index[5] + ':' + co)
        self.label6.setText(index[5] + ':' + co)
        self.gl.addWidget(self.label6, 9 - 1, 0, 1, 1)

        # ATTR7
        self.label7 = QLabel(index[6] + ':' + o3)
        self.label7.setText(index[6] + ':' + o3)
        self.gl.addWidget(self.label7, 10 - 1, 0, 1, 1)

        self.hl.addWidget(self.widget)
        vs = QSpacerItem(15, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gl.addItem(vs, 11, 0, 1, 2)
        self.combobox_type = QComboBox()
        self.combobox_type.currentIndexChanged.connect(self.reload_canvas)
        self.combobox_type.addItems(['饼图', '柱状图', '折线图', '折线、柱状图'])
        self.gl.addWidget(self.combobox_type, 12, 0, 1, 2)
        self.combobox_theme = QComboBox()
        self.combobox_theme.currentTextChanged.connect(self.change_theme)
        self.combobox_theme.addItems(['light', 'dark'])
        self.gl.addWidget(self.combobox_theme, 13, 0, 1, 2)
        # 添加web view
        self.view = QWebEngineView()
        self.view.setContextMenuPolicy(Qt.NoContextMenu)
        self.hl.addWidget(self.view)

    def addNum(self):
        city = self.nameLineEdit.text()
        location = city
        value['location'] = location
        #print(value)
        areq_2 = requests.get(aurl, params=value)
        cityid = areq_2.json()['location'][0]['id']
        value['location'] = cityid
        #print(cityid)
        ajs_2 = requests.get(yburl, params=value).json()  # ajs是当下的天气情况
        #print(ajs_2['now']['aqi'])
        self.label1.setText(index[0]+' : '+ajs_2['now']['aqi'])
        self.label2.setText(index[1]+' : '+ajs_2['now']['pm10'])
        self.label3.setText(index[2]+' : '+ajs_2['now']['pm2p5'])
        self.label4.setText(index[3]+' : '+ajs_2['now']['no2'])
        self.label5.setText(index[4]+' : '+ajs_2['now']['so2'])
        self.label6.setText(index[5]+' : '+ajs_2['now']['co'])
        self.label7.setText(index[6]+' : '+ajs_2['now']['o3'])

        global history
        history = []
        for i in range(0, 7):
            value['date'] = week_ago[i]
            history_js = requests.get(history_url, params=value).json()
            # print(json.dumps(history_js, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))
            # print(history_js['airHourly'][0]['aqi'])
            history.append(history_js['airHourly'][0]['aqi'])

        self.reload_canvas()


    def change_theme(self, theme):
        if not self.view:
            return
        options = self.get_options()
        if not options:
            return
        self.view.page().runJavaScript(
            f'''
                myChart.dispose();
                var myChart = echarts.init(document.getElementById('container'), '{theme}', {{renderer: 'canvas'}});
                myChart.clear();
                var option = eval({options});
                myChart.setOption(option);
            '''
        )

    def load_url(self):
        url = QUrl("file:///template.html")
        self.view.load(url)
        self.view.loadFinished.connect(self.set_options)

    def reload_canvas(self):
        if not self.view:
            return
            # 重载画布
        options = self.get_options()
        if not options:
            return
        self.view.page().runJavaScript(
            f'''
                myChart.clear();
                var option = eval({options});
                myChart.setOption(option);
            '''
        )

    def set_options(self):
        if not self.view:
            return
        if not self.echarts:
            # 初始化echarts
            self.view.page().runJavaScript(
                '''
                    var myChart = echarts.init(document.getElementById('container'), 'light', {renderer: 'canvas'});
                '''
            )
            self.echarts = True

        options = self.get_options()
        if not options:
            return

        self.view.page().runJavaScript(
            f'''
                var option = eval({options});
                myChart.setOption(option);
            '''
        )

    def get_options(self):

        v = history
        if self.combobox_type.currentIndex() == 0:
            # 饼图
            options = self.create_pie(v)
        elif self.combobox_type.currentIndex() == 1:
            # 柱状图
            options = self.create_bar(v)
        elif self.combobox_type.currentIndex() == 2:
            # 折线图
            options = self.create_line(v)
        elif self.combobox_type.currentIndex() == 3:
            # 折线、柱状图
            options = self.create_line_bar(v)
        else:
            return
        return options

    def create_pie(self, v):
        self.pie = Pie(TITLE_TEXT, TITLE_SUBTEXT)
        self.pie.add("天气AQI情况", ATTR, v, is_label_show=True)
        snippet = TRANSLATOR.translate(self.pie.options)
        options = snippet.as_snippet()
        return options

    def create_bar(self, v):
        self.bar = Bar(TITLE_TEXT, TITLE_SUBTEXT)
        self.bar.add('过去七天的天气AQI', ATTR, v, is_more_utils=True)
        snippet = TRANSLATOR.translate(self.bar.options)
        options = snippet.as_snippet()
        return options

    def create_line(self, v):
        self.line = Line(TITLE_TEXT, TITLE_SUBTEXT)
        self.line.add("天气AQI", ATTR, v, is_smooth=True, mark_line=["max", "average"])
        snippet = TRANSLATOR.translate(self.line.options)
        options = snippet.as_snippet()
        return options

    def create_line_bar(self, v):
        today = DT.date.today()
        week_ago = ["20" + (today - DT.timedelta(days=i)).strftime("%y%m%d") for i in range(1, 8)]
        week_ago.reverse()

        line = Line(TITLE_TEXT, TITLE_SUBTEXT)
        line.add("天气", ATTR, v, is_smooth=True, mark_line=["max", "average"])
        bar = Bar(TITLE_TEXT, TITLE_SUBTEXT)
        bar.add('天气', ATTR, v, is_more_utils=True)

        overlap = Overlap()
        overlap.add(line)
        overlap.add(bar)
        snippet = TRANSLATOR.translate(overlap.options)
        options = snippet.as_snippet()
        return options


if __name__ == '__main__':
    import sys

    today = DT.date.today()
    ATTR_2 = ["20" + (today - DT.timedelta(days=i)).strftime("%y%m%d") for i in range(1, 8)]
    ATTR_2.reverse()

    ATTR = [(today - DT.timedelta(days=i)).strftime("%y%m%d")[2:] for i in range(1, 8)]
    ATTR.reverse()

    location = 'beijing'
    value['location'] = location
    areq = requests.get(aurl, params=value)
    cityid = areq.json()['location'][0]['id']
    value['location'] = cityid
    ajs = requests.get(yburl, params=value).json()  # ajs是当下的天气情况
    AQI = ajs['now']['aqi']
    pm10 = ajs['now']['pm10']
    pm2p5 = ajs['now']['pm2p5']
    no2 = ajs['now']['no2']
    so3 = ajs['now']['so2']
    co = ajs['now']['co']
    o3 = ajs['now']['o3']

    week_ago = ["20" + (today - DT.timedelta(days=i)).strftime("%y%m%d") for i in range(1, 8)]
    week_ago.reverse()


    for i in range(0, 7):
        value['date'] = week_ago[i]
        history_js = requests.get(history_url, params=value).json()
        # print(json.dumps(history_js, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))
        #print(history_js['airHourly'][0]['aqi'])
        history.append(history_js['airHourly'][0]['aqi'])

    app = QApplication(sys.argv)
    app.setStyle('fusion')
    form_click = Form()
    form_click.show()

    sys.exit(app.exec_())