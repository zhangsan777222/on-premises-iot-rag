# -*- coding: utf-8 -*-
"""生成一份《IoT-2000 物联网环境监测网关 用户手册》PDF，作为 RAG 导入语料。

用法: python make_sample_manual.py
输出: data/iot_gateway_manual.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.lib import colors

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "iot_gateway_manual.pdf")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="STSong-Light",
                    fontSize=17, leading=24, spaceAfter=10, textColor=colors.HexColor("#0B5394"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="STSong-Light",
                    fontSize=13, leading=20, spaceBefore=8, spaceAfter=6,
                    textColor=colors.HexColor("#1155CC"))
BODY = ParagraphStyle("BODY", parent=styles["BodyText"], fontName="STSong-Light",
                      fontSize=10.5, leading=17, spaceAfter=5)
TITLE = ParagraphStyle("TITLE", parent=styles["Title"], fontName="STSong-Light",
                       fontSize=26, leading=36, alignment=TA_CENTER,
                       textColor=colors.HexColor("#0B5394"))
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontName="STSong-Light",
                     fontSize=12, leading=20, alignment=TA_CENTER)


def tbl(data, widths):
    t = Table(data, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "STSong-Light", 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA7B8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


story = []
A = story.append

# ---------------- 封面 ----------------
A(Spacer(1, 40 * mm))
A(Paragraph("IoT-2000", TITLE))
A(Paragraph("物联网环境监测网关  用户手册", TITLE))
A(Spacer(1, 12 * mm))
A(Paragraph("文档版本：V2.3", SUB))
A(Paragraph("适用固件：V1.8.0 及以上", SUB))
A(Paragraph("发布日期：2025-03-15", SUB))
A(Spacer(1, 30 * mm))
A(Paragraph("深圳市智联感知科技有限公司", SUB))
A(PageBreak())

# ---------------- 1 产品概述 ----------------
A(Paragraph("1. 产品概述", H1))
A(Paragraph(
    "IoT-2000 是一款面向工业现场的低功耗物联网环境监测网关，内置 4G Cat.1 与 Wi-Fi 双模通信模块，"
    "可同时接入温度、湿度、PM2.5、CO2、光照、噪声等六类环境传感器，并将采集数据通过 MQTT、"
    "HTTP 或 Modbus TCP 协议上传至云平台或本地服务器。设备采用 32 位工业级 MCU，支持断网缓存、"
    "边缘阈值告警、远程固件升级（OTA）等能力，适用于智慧农业、仓储物流、机房监控、园区环境监测等场景。",
    BODY))
A(Paragraph("1.1 主要特性", H2))
for s in [
    "支持 6 路传感器输入（4 路 RS485 + 2 路 4-20mA 模拟量）；",
    "通信方式：4G Cat.1、Wi-Fi 2.4GHz、以太网 10/100M；",
    "支持 MQTT 3.1.1 / MQTT over TLS，支持 HTTP(S) 上报；",
    "内置 8MB 本地缓存，断网可缓存不少于 72000 条记录；",
    "支持 Modbus RTU 主站采集，最多挂载 32 个从站；",
    "工作温度 -30℃ ~ +70℃，防护等级 IP65（配防水外壳）；",
    "宽压供电 DC 9~36V，支持太阳能 + 锂电池备份供电。",
]:
    A(Paragraph("• " + s, BODY))

# ---------------- 2 硬件规格 ----------------
A(Paragraph("2. 硬件规格", H1))
A(tbl([
    ["项目", "参数"],
    ["型号", "IoT-2000"],
    ["主控", "ARM Cortex-M4 32 位 MCU，主频 120MHz"],
    ["存储", "Flash 16MB / RAM 512KB，外置 8MB 数据缓存芯片"],
    ["供电", "DC 9~36V（典型 12V），功耗 ≤ 2.5W"],
    ["4G 制式", "LTE Cat.1，支持移动/联通/电信全网通"],
    ["Wi-Fi", "2.4GHz 802.11 b/g/n，支持 AP/STA 模式"],
    ["以太网", "1 路 RJ45，10/100Mbps 自适应"],
    ["RS485", "4 路，隔离电压 2500V，波特率 1200~115200"],
    ["模拟量输入", "2 路 4-20mA，12 位 ADC 精度"],
    ["工作温度", "-30℃ ~ +70℃"],
    ["存储温度", "-40℃ ~ +85℃"],
    ["外形尺寸", "145mm × 95mm × 40mm（不含天线）"],
    ["重量", "约 320g"],
], [45 * mm, 115 * mm]))
A(Spacer(1, 4 * mm))

# ---------------- 3 接口与指示灯 ----------------
A(Paragraph("3. 接口与指示灯说明", H1))
A(Paragraph("3.1 接口定义", H2))
A(tbl([
    ["接口标识", "类型", "说明"],
    ["PWR", "DC 圆孔 5.5×2.1", "电源输入 9~36V，内正外负"],
    ["RS485-1~4", "凤凰端子 A/B/GND", "接 Modbus 传感器，A 正 B 负"],
    ["AI1 / AI2", "2 位端子", "4-20mA 模拟量输入，需外供 24V"],
    ["LAN", "RJ45", "以太网口，支持 PoE 受电（选配）"],
    ["SIM", "Nano SIM 卡槽", "插入 4G 物联网卡，芯片朝下"],
    ["USB", "Type-C", "本地调试与固件升级"],
    ["RESET", "内嵌按键", "长按 8 秒恢复出厂设置"],
], [30 * mm, 42 * mm, 88 * mm]))
A(Spacer(1, 3 * mm))
A(Paragraph("3.2 指示灯状态", H2))
A(tbl([
    ["指示灯", "颜色", "状态", "含义"],
    ["PWR", "红", "常亮", "供电正常"],
    ["PWR", "红", "闪烁", "供电电压异常（低于 8.5V）"],
    ["NET", "绿", "常亮", "已连接云平台"],
    ["NET", "绿", "1Hz 闪烁", "注册网络成功，未连接平台"],
    ["NET", "绿", "快闪 5Hz", "正在搜索网络 / 无信号"],
    ["COM", "蓝", "闪烁", "正在与传感器通信"],
    ["ERR", "黄", "常亮", "传感器采集或上报失败"],
], [24 * mm, 18 * mm, 30 * mm, 88 * mm]))
A(Spacer(1, 4 * mm))

# ---------------- 4 安装步骤 ----------------
A(Paragraph("4. 安装与接线步骤", H1))
for i, s in enumerate([
    "断开电源，确认现场无带电作业风险；",
    "将 4G 天线、Wi-Fi 天线旋入对应 SMA 接口并拧紧；",
    "将 Nano SIM 卡按图示方向插入卡槽，听到“咔”声即到位；",
    "按端子定义连接电源与传感器，务必确认 A/B 线序正确，接反会导致通信失败；",
    "接通 DC 12V 电源，观察 PWR 指示灯常亮；",
    "等待 30~60 秒，NET 指示灯由快闪转为常亮，表示已连接平台；",
    "使用手机扫描机身二维码，进入配网页面完成设备绑定。",
], 1):
    A(Paragraph(f"{i}. {s}", BODY))
A(Paragraph("注意：传感器电缆建议使用屏蔽双绞线，屏蔽层单端接地，通信线尽量远离动力电缆，"
            "以避免电磁干扰造成数据跳变。", BODY))

# ---------------- 5 网络与平台配置 ----------------
A(Paragraph("5. 网络与平台配置", H1))
A(Paragraph("5.1 配网方式", H2))
A(Paragraph(
    "设备支持三种配网方式：① 以太网直连；② 4G 自动拨号（插入 SIM 卡后上电自动注册）；"
    "③ Wi-Fi 配网（默认进入 AP 模式，SSID 为 IoT2000-XXXX，初始密码 12345678，"
    "浏览器访问 192.168.4.1 进入配置页）。", BODY))
A(Paragraph("5.2 MQTT 上报参数", H2))
A(tbl([
    ["参数项", "默认值", "取值范围"],
    ["Broker 地址", "mqtt.zhilian-iot.com", "域名或 IP"],
    ["Broker 端口", "1883（TLS 8883）", "1~65535"],
    ["ClientID", "设备 SN 号", "自定义"],
    ["上报主题", "/dev/{SN}/upload", "自定义"],
    ["下发主题", "/dev/{SN}/command", "自定义"],
    ["默认上报间隔", "60 秒", "10~3600 秒"],
    ["心跳间隔", "120 秒", "30~600 秒"],
], [42 * mm, 58 * mm, 60 * mm]))
A(Spacer(1, 3 * mm))
A(Paragraph("5.3 上报数据格式（JSON）", H2))
A(Paragraph(
    '{"sn":"IT2000123456","ts":1710489600,"temp":23.5,"humi":58.2,' 
    '"pm25":35,"co2":620,"lux":340,"noise":42.1,"rssi":-67}', BODY))

# ---------------- 6 Modbus 寄存器 ----------------
A(Paragraph("6. Modbus RTU 寄存器表", H1))
A(Paragraph("设备作为 Modbus 主站轮询从站，采样结果映射到内部寄存器，可通过 Modbus TCP 读取：", BODY))
A(tbl([
    ["寄存器地址", "名称", "数据类型", "单位", "说明"],
    ["0x0000", "温度", "int16", "0.1℃", "有符号，例 235=23.5℃"],
    ["0x0001", "湿度", "uint16", "0.1%RH", "例 582=58.2%RH"],
    ["0x0002", "PM2.5", "uint16", "μg/m³", "量程 0~1000"],
    ["0x0003", "CO2", "uint16", "ppm", "量程 400~5000"],
    ["0x0004", "光照", "uint32", "lux", "占 2 个寄存器"],
    ["0x0006", "噪声", "uint16", "0.1dB", "例 421=42.1dB"],
    ["0x0007", "设备状态", "uint16", "位掩码", "bit0 网络,bit1 平台"],
    ["0x0010", "上报间隔", "uint16", "秒", "可写，10~3600"],
], [26 * mm, 24 * mm, 24 * mm, 20 * mm, 66 * mm]))
A(Spacer(1, 3 * mm))
A(Paragraph("读寄存器示例（Modbus RTU，从站地址 1，读温度）："
            "01 03 00 00 00 01 84 0A", BODY))

# ---------------- 7 故障排查 ----------------
A(Paragraph("7. 常见故障与排查", H1))
A(tbl([
    ["现象", "可能原因", "处理方法"],
    ["PWR 不亮", "电源未接好/电压不足", "检查接线，确认电压 ≥9V"],
    ["NET 一直快闪", "无信号或 SIM 卡异常", "检查天线、SIM 是否欠费/装反"],
    ["NET 闪烁不常亮", "Broker 地址或端口错误", "核对 MQTT 参数与防火墙策略"],
    ["数据为 0 或跳变", "RS485 线序接反或干扰", "对调 A/B，使用屏蔽线单端接地"],
    ["ERR 常亮", "某路传感器离线", "逐个断开排查，确认从站地址冲突"],
    ["频繁掉线", "Wi-Fi 信号弱", "改用 4G 或调整天线位置"],
    ["无法配网", "密码错误/浏览器缓存", "复位后重试，访问 192.168.4.1"],
], [34 * mm, 58 * mm, 68 * mm]))
A(Spacer(1, 3 * mm))

# ---------------- 8 技术参数与售后 ----------------
A(Paragraph("8. 技术参数汇总", H1))
A(tbl([
    ["项目", "指标"],
    ["采集精度", "温度 ±0.3℃，湿度 ±3%RH，CO2 ±50ppm"],
    ["采样周期", "1~600 秒可配置，默认 10 秒"],
    ["缓存能力", "≥72000 条（8MB）"],
    ["通信加密", "支持 TLS1.2、AES-128"],
    ["平均无故障时间", "MTBF ≥ 50000 小时"],
    ["认证", "CE、FCC、SRRC、RoHS"],
    ["防护等级", "IP65（配防水外壳时）"],
    ["保修期", "整机 2 年，传感器 1 年"],
], [45 * mm, 115 * mm]))
A(Spacer(1, 3 * mm))
A(Paragraph("9. 售后服务", H1))
A(Paragraph("技术支持邮箱：support@zhilian-iot.com　服务热线：400-800-1234（工作日 9:00-18:00）。"
            "返修前请先联系技术支持获取 RMA 编号，并随设备附上故障描述与购买凭证。", BODY))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=25 * mm, rightMargin=25 * mm,
                        topMargin=22 * mm, bottomMargin=20 * mm,
                        title="IoT-2000 物联网环境监测网关 用户手册")
doc.build(story)
print("已生成:", OUT)
