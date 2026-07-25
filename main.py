from typing import Any
from zipfile import ZipFile
from pathlib import Path
from io import BytesIO
from dissect.eventlog.evtx import Evtx


class GetSystemInfoParser:

    def __init__(self):
        self.result = {}
        self.gsi6directory = Path('./')
        self.gsi6prefix = ('GSI6',  "report", "GetSystemInfo", "GSI", "GSI5")
        self.gsi5prefix = 'GetSystemInfo'
        self.gsi5keywords = ['<Time>', '<BIOS>', '<Processor>', '<OperatingSystem>', '<ComputerSystem>',
                        '<Environment>', '<Registry>', "<VideoController>"]
        self.gsi5keywords2 = ['<InstalledProduct>', '<Process>']

    def get_reports(self) -> list:
        #  Поиск всех отчетов GSI6 в текущем каталоге
        gsi6reports = []
        for file_path in self.gsi6directory.iterdir():
            if file_path.is_file() and file_path.name.startswith(self.gsi6prefix):
                gsi6reports.append(file_path.name)
        return gsi6reports

    def main_reading_thread(self, txt: list, net_diag=None, evt_kel=None, evt_sys=None, evt_app=None):
        gsi5_correct_flag = False
        self.result = {"AVState": {
            "Protection_AvInstalled": "0",
            "Protection_AvRunning": "0",
            "Protection_BasesDate": "",
            "Protection_LastFscan": "",
            "Protection_LastConnected": "",
            "Protection_DynamicVM": "0",
            "Protection_ExternalTenantId": ""
        }}
        if txt == "Unknown":
            return "Unknown"
        txt = iter(txt)

        for line in txt:
            try:
                line = line.decode("utf-8").rstrip("\r\n").strip()
            except (UnicodeDecodeError, AttributeError):
                line = line.decode("cp1251").rstrip("\r\n").strip()

            #  Если строка пустая, то пропускаем итерацию:
            if not line:
                continue

            if "GetSystemInfo version" in line:
                self.result["gsi_ver"] = line.split()[-1].strip()

            if line in self.gsi5keywords:
                self.parse_single_block(txt, line[1:-1])
                continue

            if line == "<LogicalDisk>":
                self.parse_logical_disk_block(txt, line[1:-1])
                continue

            if line == "<InstalledProduct>":
                self.parse_installed_product_block(txt, line[1:-1])
                continue

            if line == "<Process>":
                self.parse_process_block(txt, line[1:-1])
                continue

            if line == "<Services>":
                self.parse_service_block(txt, line[1:-1])
                continue

            if line == "<Network_Agent_report>":
                self.parse_network_agent_report(txt, line[1:-1])
                continue

            if line == "<AVState>":
                self.parse_single_block(txt, line[1:-1])
                continue

            if line == "<HOSTS>":
                self.parse_hosts_block(txt, line[1:-1])
                continue

            if line == "<OpenPorts>":
                self.parse_open_ports(txt)
                continue

            if line == "<NTLogEvent>":
                self.parse_event_logs(txt, line[1:-1])
                continue

            if "<MD5>" in line:
                gsi5_correct_flag = True

        if gsi5_correct_flag:
            pass
        else:
            raise Exception()

        if net_diag is not None:
            self.result["net_diag"] = ""
            net_diag = iter(net_diag)
            for line in net_diag:
                line = line.decode("utf-8").rstrip("\r\n\t").strip()
                if "wfp filters:" in line:
                    break
                if line.startswith("Command"):
                    line = f"[bold][blink]{line}[/][/]"
                self.result["net_diag"] += f" {line}\n"
        else:
            self.result["net_diag"] = """[red]
 ███████ ██ ██      ███████     ███    ██  ██████  ████████     ███████  ██████  ██    ██ ███    ██ ██████  
 ██      ██ ██      ██          ████   ██ ██    ██    ██        ██      ██    ██ ██    ██ ████   ██ ██   ██ 
 █████   ██ ██      █████       ██ ██  ██ ██    ██    ██        █████   ██    ██ ██    ██ ██ ██  ██ ██   ██ 
 ██      ██ ██      ██          ██  ██ ██ ██    ██    ██        ██      ██    ██ ██    ██ ██  ██ ██ ██   ██ 
 ██      ██ ███████ ███████     ██   ████  ██████     ██        ██       ██████   ██████  ██   ████ ██████  
[/]"""

        print(f"{self.result["InstalledProduct"]}")
        return self.result

    def parse_single_block(self, txt, current_block_name):
        """
        Предназначен только для парсинга одиночных блоков в GetSystemInfo_<...>txt, таких как:
            '<Time>', '<BIOS>', '<Processor>', '<OperatingSystem>', '<ComputerSystem>', '<Environment>', '<Registry>'
        Добавляет спаршенные результаты в self.result
        """
        if current_block_name == "AVState":
            pass
        else:
            self.result[current_block_name] = {}

        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()
            #  Если строка пустая, то идем дальше:
            if not line:
                continue
            #  Разделяем содержимое текущей строки на ключ:значение, прим: 'Manufacturer: Phoenix Technologies LTD'
            if "[:]" in line:
                key, value = line.split("[:]", 1)
                self.result[current_block_name][key] = value
                continue
            #  Если одиночный блок закончился, то возвращаем поток в основной цикл
            if line.startswith("</"):
                return

    def parse_logical_disk_block(self, txt, current_block_name: str):
        self.result[current_block_name] = {}
        caption = None
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()

            if not line:
                continue

            if "Caption[:]" in line:
                caption = line.split("[:]", 1)
                self.result[current_block_name][caption[1]] = {}
                continue

            if "[:]" in line:
                key, value = line.split("[:]", 1)
                self.result[current_block_name][caption[1]][key] = value

            if line.startswith("</"):
                return

    def parse_installed_product_block(self, txt, current_block_name: str):
        self.result[current_block_name] = []
        windows_items = ("Microsoft Visual C++", "Security Update for Microsoft", "Update for Microsoft", "GDR ", "Service Pack ",
                         "Sql Server Customer Experience", "Office 16 Click-to-Run ", "Transact-SQL ScriptDom", "T-SQL ScriptDom",
                         "Batch Parser", "Shared Management Objects Extensions", "RsFx Driver", "Tools for Office Runtime (x64)",
                         " Native Client", " XEvent", " SQL Diagnostics", " Connection Info", " Shared Management Objects", " DMF", " for SQL Server",
                         " Data-Tier Application Framework (x86)", " T-SQL Language Service")
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()

            if not line:
                continue

            if "Name[:]" in line:
                name = line.split("[:]", 1)
                if name[1].startswith(windows_items) or name[1].endswith(windows_items) or name[1] == '':
                    for i in range (0, 6):
                        next(txt)
                else:
                    self.result[current_block_name].append({
                        "Name": name[-1],
                        "Uninstall": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "Vendor": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "Version": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "InstallDate": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "InstallLocation": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "Language": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    })
                    continue

            if line.startswith("</"):
                return

    def parse_process_block(self, txt, current_block_name: str):
        self.result[current_block_name] = []
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()

            if line.startswith("</"):
                return

            if not line:
                continue

            if "||" in line and line.startswith("Modules[:]") != True:
                process = line.split("||")
                if len(process) > 4:
                    self.result[current_block_name].append({
                        "Process": process[0],
                        "Version_dev": process[1],
                        "Version": process[2],
                        "FullName": process[-4],
                    })
                continue

            if line == "CommandLine[:]":
                for _ in range(0, 8):
                    next(txt, None)

    def parse_service_block(self, txt, current_block_name: str):
        self.result[current_block_name] = []
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()

            if line.startswith("</"):
                return

            if not line:
                continue

            if "||" in line and line.startswith("Modules[:]") != True:
                service = line.split("||")
                self.result[current_block_name].append({
                    "Service": service[0],
                    "Version_dev": service[1],
                    "Version": service[2],
                    "FullName": service[-4],
                    "Pathname": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Name": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "ServiceType": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "ProcessID": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "AcceptPause": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "AcceptStop": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Description": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "DisplayName": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Started": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "StartMode": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "StopName": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "State": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Status": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                })
                continue

            if line == "CommandLine[:]":
                for _ in range(0, 8):
                    next(txt, None)

    def parse_hosts_block(self, txt, current_block_name: str):
        self.result[current_block_name] = ""
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()
            if line.startswith("</"):
                return
            elif line.endswith(f"</{current_block_name}>"):
                line = line.strip(f"</{current_block_name}>")
                self.result[current_block_name] = self.result[current_block_name] + line + "\n"
                return
            else:
                self.result[current_block_name] = self.result[current_block_name] + line + "\n"

    def parse_open_ports(self, txt):
        self.result["OpenPorts"] = []
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()
            if line.startswith("</"):
                return
            if len(line.split("<||||>")) == 4:
                line_local = line.split("<||||>")
                self.result["OpenPorts"].append({
                    "Process": line_local[1].split("||")[0],
                    "Protocol": line_local[0],
                    "Source_ip": line_local[2],
                    "Source_port": line_local[3],
                    "Destination_ip": "",
                    "Destination_port": "",
                    "Status": "",
                })
            elif len(line.split("<||||>")) == 7:
                if len(line.split("||")) > 20:
                    line_local = line.split("<||||>")
                    self.result["OpenPorts"].append({
                        "Process": line_local[1].split("||", 1)[0],
                        "Protocol": line_local[0],
                        "Source_ip": line_local[-5],
                        "Source_port": line_local[-4],
                        "Destination_ip": line_local[-3],
                        "Destination_port": line_local[-2],
                        "Status": line_local[-1],
                    })
                elif len(line.split("||")) == 13:
                    line_local = line.split("<||||>")
                    self.result["OpenPorts"].append({
                        "Process": line_local[1],
                        "Protocol": line_local[0],
                        "Source_ip": line_local[2],
                        "Source_port": line_local[3],
                        "Destination_ip": line_local[4],
                        "Destination_port": line_local[5],
                        "Status": line_local[6],
                    })
            else:
                continue

    def parse_network_agent_report(self, txt, current_block_name: str):
        self.result[current_block_name] = ""
        for line in txt:
            try:
                line = line.decode("cp1251").rstrip("\r\n").strip()
            except UnicodeDecodeError:
                line = line.decode("utf-8").rstrip("\r\n").strip()
            if line.startswith("</"):
                return
            else:
                if line.startswith("Дата/время"):
                    first, two = line.split(":", 1)
                    self.result[current_block_name] = self.result[current_block_name] + "\n" + first
                    self.result[current_block_name] = self.result[current_block_name] + "\n" + two.strip()
                else:
                    self.result[current_block_name] = self.result[current_block_name] + "\n" + line

    def parse_event_logs(self, txt, current_block_name: str):
        self.result[current_block_name] = []
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()
            if line.startswith("</"):
                return
            if "Category[:]" in line:
                self.result[current_block_name].append({
                    "Category": line.split("[:]")[-1],
                    "CategoryString": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Event_code": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "EventIdentifier": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "EventType": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Log_file": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Message": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "RecordNumber": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Source_name": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Time": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "TimeWritten": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Type": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "User": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                })

    @staticmethod
    def parse_evt_file(evt_bytes):
        parsed_records = []
        sanitized_record = {}
        log_file = Evtx(evt_bytes)

        for record in log_file:
            # Пытаемся преобразовать коллекцию в словарь через внутренний метод ._asdict()
            # Если метод недоступен, собираем словарь вручную из итератора
            if hasattr(record, "_asdict"):
                record_dict = record._asdict()
            else:
                record_dict = dict(record.items()) if hasattr(record, "items") else dict(record)

            # Приводим типы к строкам для безопасной сериализации
            for key, value in record_dict.items():
                if isinstance(value, (bytes, bytearray)):
                    sanitized_record[key] = value.hex()
                elif hasattr(value, "__str__"):
                    sanitized_record[key] = str(value)
                else:
                    sanitized_record[key] = value

            parsed_records.append(sanitized_record)

        return parsed_records

    @staticmethod
    def open_gsi5txt_inside_gsi6zip(gsi6_file_name: str):
        r"""
        Принимает название файла GSI6.
        :return: IO[bytes]
            Возвращает текстовый файл GetSystemInfo...txt в формате списка.
        """
        gsi5_txt, net_diag, evt_kel, evt_sys, evt_app = "", None, False, False, False
        with ZipFile(gsi6_file_name) as archive:
            inner_getsysteminfo = next(
                (
                    name for name in archive.namelist()
                    if name.startswith("GetSystemInfo") and name.endswith(".zip")
                ),
                None,
            )

            with archive.open(inner_getsysteminfo) as archive_inner:
                with ZipFile(BytesIO(archive_inner.read())) as inner:
                    with inner.open(inner.namelist()[0]) as txt:
                        gsi5_txt = txt.readlines()

            if "Network_diagnostics.txt" in archive.namelist():
                for name in archive.namelist():
                    if name.startswith("Network_diagnostics"):
                        with archive.open(name) as txt:
                            net_diag = txt.readlines()

            if "Eventlogs/Kaspersky Event Log.evt" in archive.namelist():
                with BytesIO(archive.read("Eventlogs/Kaspersky Event Log.evt")) as evt:
                    try:
                        evt_kel = True
                    except:
                        evt_kel = False

            if "Eventlogs/System.evt" in archive.namelist():
                with BytesIO(archive.read("Eventlogs/System.evt")) as evt:
                    try:
                        evt_sys = True
                    except:
                        evt_sys = False

            if "Eventlogs/Application.evt" in archive.namelist():
                with BytesIO(archive.read("Eventlogs/Application.evt")) as evt:
                    try:
                        evt_app = True
                    except:
                        evt_app = False

            return gsi5_txt, net_diag, evt_kel, evt_sys, evt_app

    @staticmethod
    def open_gsi5txt(gsi_file_name: str) -> list[bytes]:
        with open(gsi_file_name, "rb") as txt:
            # readed = []
            # for line in txt:
            #     try:
            #         line = line.decode("utf-8").strip()
            #     except UnicodeDecodeError, AttributeError:
            #         line = line.decode("ansi").strip()
            #     readed.append(line)
            return txt.readlines()

    @staticmethod
    def open_gsi5zip(gsi_file_name: str) -> list[bytes]:
        with ZipFile(gsi_file_name) as archive:
            with archive.open(archive.namelist()[0]) as txt:
                return txt.readlines()

    @staticmethod
    def get_information_from_gsi(gsi_file_name):
        if gsi_file_name.endswith(".txt"):
            with open(gsi_file_name, "r+", encoding="utf-8") as f:
                if "GetSystemInfo version" in f.readline():
                    gsi_out = GetSystemInfoParser.open_gsi5txt(gsi_file_name)
                    return gsi_out, None, None, None, None
        elif gsi_file_name.endswith(".zip"):
            with ZipFile(gsi_file_name) as archive:
                if len(archive.namelist()) == 1 and archive.namelist()[0].startswith("GetSystemInfo"):
                    gsi_out = GetSystemInfoParser.open_gsi5zip(gsi_file_name)
                    return gsi_out, None, None, None, None
                else:
                    for name in archive.namelist():
                        if name.startswith("GetSystemInfo") and name.endswith(".zip"):
                            return GetSystemInfoParser.open_gsi5txt_inside_gsi6zip(gsi_file_name)
        return "Unknown", None, None, None, None


if __name__ == "__main__":
    bigc = GetSystemInfoParser()
    reports_list = bigc.get_reports()
    txt, net_diag, evt_kel, evt_sys, evt_app = bigc.get_information_from_gsi(reports_list[7])
    bigc.main_reading_thread(txt, net_diag, evt_kel, evt_sys, evt_app)
    print(f"\n\n{reports_list}")