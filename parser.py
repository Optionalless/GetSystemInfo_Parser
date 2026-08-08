from zipfile import ZipFile
from pathlib import Path
from io import BytesIO
from dissect.eventlog.evtx import Evtx


class GetSystemInfoParser:

    def __init__(self):
        self.result = {
            "Time": {},
            "BIOS": {
                "BuildNumber": "",
                "InstallDate": '',
                "Manufacturer": '',
                "Name": '',
                "PrimaryBIOS": '',
                "ReleaseDate": '',
                "SerialNumber": '',
                "SMBIOSBIOSVersion": '',
                "SMBIOSMajorVersion": '',
                "SMBIOSMinorVersion": '',
                "SMBIOSPresent": '',
                "SoftwareElementID": '',
                "SoftwareElementState": '',
                "Status": '',
                "TargetOperatingSystem": '',
                "Version": ''
            },
            "Processor": {
                "AddressWidth": '',
                "Architecture": '',
                "Availability": '',
                "Caption": '',
                "CpuStatus": '',
                "CurrentClockSpeed": '',
                "CurrentVoltage": '',
                "DataWidth": '',
                "Description": '',
                "DeviceID": '',
                "Family": '',
                "LastErrorCode": '',
                "Level": '',
                "LoadPercentage": '',
                "Manufacturer": '',
                "MaxClockSpeed": '',
                "Name": '',
                "NumberOfCores": '',
                "NumberOfLogicalProcessors": '',
                "ProcessorType": '',
                "Role": '',
                "SocketDesignation": '',
                "Status": '',
                "StatusInfo": '',
                "Stepping": '',
                "SystemName": '',
                "UpgradeMethod": '',
                "Version": '',
                "VoltageCaps": ''
            },
            "OperatingSystem": {
                "BootDevice": '',
                "BuildNumber": '',
                "BuildType": '',
                "Caption": '',
                "CountryCode": '',
                "CSDVersion": '',
                "Description": '',
                "FreePhysicalMemory": '',
                "FreeSpaceInPagingFiles": '',
                "FreeVirtualMemory": '',
                "InstallDate": '',
                "LastBootUpTime": '',
                "LocalDateTime": '',
                "Manufacturer": '',
                "MUILanguages": '',
                "NumberOfProcesses": '',
                "NumberOfUsers": '',
                "OSArchitecture": '',
                "OSLanguage": '',
                "ServicePackMajorVersion": '',
                "ServicePackMinorVersion": '',
                "SizeStoredInPagingFiles": '',
                "SystemDevice": '',
                "SystemDirectory": '',
                "TotalVirtualMemorySize": '',
                "TotalVisibleMemorySize": '',
                "Version": '',
                "WindowsDirectory": ''
            },
            "ComputerSystem": {
                "BootupState": '',
                "DNSHostName": '',
                "Domain": '',
                "DomainRole": '',
                "Manufacturer": '',
                "Model": '',
                "NetworkServerModeEnabled": '',
                "PartOfDomain": '',
                "PCSystemType": '',
                "Status": '',
                "SupportContactDescription": '',
                "SystemType": '',
                "UserName": '',
                "Workgroup": ''
            },
            "Environment": {},
            "Printer": {},
            "VideoController": {},
            "DesktopMonitor": {},
            "SoundDevice": {},
            "NTLogEvent": [],
            "LogicalDisk": {},
            "InstalledProduct": [],
            "Process": [],
            "Services": [],
            "SystemDriver": [],
            "Registry": {},
            "BHO": '',
            "PnPSignedDriver": [],
            "Share": {},
            "OpenPorts": [],
            "HOSTS": '',
            "AVState": {
                "Protection_AdmServer": "",
                "Protection_HostId": "",
                "Protection_AvInstalled": "0",
                "Protection_AvRunning": "0",
                "Protection_BasesDate": "",
                "Protection_LastFscan": "",
                "Protection_LastConnected": "",
                "Protection_NagentVersion": "",
                "Protection_NagentFullVersion": "",
                "Protection_DynamicVM": "0",
                "Protection_ExternalTenantId": "",
                "Protection_RtpState": "",
                "Protection_HasRtp": ""
            },
            "Network_Agent_report": '[red] klnagchk output not found'
        }
        self.gsi6directory = Path('./')
        self.gsi_prefix = ("report", "GetSystemInfo", "GSI", "getsysteminfo", "gsi")
        self.gsi_endfix = (".zip", ".txt")
        self.gsi5prefix = 'GetSystemInfo'
        self.gsi5keywords = ['<Time>', '<BIOS>', '<Processor>', '<OperatingSystem>', '<ComputerSystem>',
                        '<Environment>', '<Registry>', "<VideoController>"]
        self.gsi5keywords2 = ['<InstalledProduct>', '<Process>']

    def get_reports(self) -> list:
        #  Поиск всех отчетов GSI6 в текущем каталоге
        gsi6reports = []
        for file_path in self.gsi6directory.iterdir():
            if file_path.is_file() and file_path.name.startswith(self.gsi_prefix) and file_path.name.endswith(self.gsi_endfix):
                gsi6reports.append(file_path.name)
        return gsi6reports

    def main_reading_thread(self, txt: list, net_diag=None, kl_version_hotfix=None, filter_manager=None):
        gsi5_correct_flag = False

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

            if line == "<SystemDriver>":
                self.parse_system_driver_block(txt, line[1:-1])
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
            self.result["net_diag"] = "[red] File not found[/]"

        if kl_version_hotfix is not None:
            self.result["KL_Version_Hotfix"] = "[red]No patches installed[/]"
            kl_version_hotfix = iter(kl_version_hotfix)
            for line in kl_version_hotfix:
                line = line.decode("utf-8").rstrip("\r\n\t").strip()
                if line.startswith("ProductHotfix"):
                    self.result["KL_Version_Hotfix"] = f"[green]{line.split(":", 1)[-1].strip()}[/]"
        else:
            self.result["KL_Version_Hotfix"] = "[red]File not found[/]"

        if filter_manager is not None:
            self.result["filter_manager"] = ""
            filter_manager = iter(filter_manager)
            for line in filter_manager:
                line = line.decode("utf-8").rstrip("\r\n\t").strip()
                if line.startswith("Command"):
                    line = f"[bold][blink]{line}[/][/]"
                self.result["filter_manager"] += f" {line}\n"
        else:
            self.result["filter_manager"] = "[red] File not found[/]"

        print(f"{self.result["SystemDriver"]}")
        return self.result

    def parse_single_block(self, txt, current_block_name):
        """
        Предназначен только для парсинга одиночных блоков в GetSystemInfo_<...>txt, таких как:
            '<Time>', '<BIOS>', '<Processor>', '<OperatingSystem>', '<ComputerSystem>', '<Environment>', '<Registry>'
        Добавляет спаршенные результаты в self.result
        """
        # if current_block_name == "AVState":
        #     pass
        # else:
        #     self.result[current_block_name] = {}

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
        # self.result[current_block_name] = {}
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
        num = 0
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
                        "Num": num,
                        "Name": name[-1],
                        "Uninstall": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "Vendor": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "Version": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "InstallDate": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "InstallLocation": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                        "Language": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    })
                    num += 1
                    continue

            if line.startswith("</"):
                return

    def parse_process_block(self, txt, current_block_name: str):
        num = 0
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
                        "Num": num,
                        "Process": process[0],
                        "Version_dev": process[1],
                        "Version": process[2],
                        "FullName": process[-4],
                    })
                    num += 1
                continue

            if line == "CommandLine[:]":
                for _ in range(0, 8):
                    next(txt, None)

    def parse_system_driver_block(self, txt, current_block_name: str):
        num = 0
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()

            if line.startswith("</"):
                return

            if not line:
                continue

            if line.startswith("AcceptPause[:]"):
                driver = {
                    "Num": num,
                    "AcceptPause": line.split("[:]")[-1].strip(),
                    "AcceptStop": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Caption": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Description": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Name": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "PathName": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "ServiceType": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Started": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "StartMode": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "State": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                    "Status": next(txt, None).decode("utf-8").rstrip("\r\n").strip().split("[:]")[-1],
                }
                self.result[current_block_name].append(driver)
                num += 1
                continue

    def parse_service_block(self, txt, current_block_name: str):
        num = 0
        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()

            if line.startswith("</"):
                return

            if not line:
                continue

            if "||" in line and line.startswith("Modules[:]") != True:
                service = line.split("||")
                self.result[current_block_name].append({
                    "Num": num,
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
                num += 1
                continue

            if line == "CommandLine[:]":
                for _ in range(0, 8):
                    next(txt, None)

    def parse_hosts_block(self, txt, current_block_name: str):
        # self.result[current_block_name] = ""
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
        # self.result["OpenPorts"] = []
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
        self.result["Network_Agent_report"] = ""
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
                    self.result[current_block_name] = self.result[current_block_name] + "\n" + f" {first}"
                    self.result[current_block_name] = self.result[current_block_name] + "\n" + f" {two.strip()}"
                else:
                    self.result[current_block_name] = self.result[current_block_name] + "\n" + f" {line}"

    def parse_event_logs(self, txt, current_block_name: str):
        last_string_name = 'Other'
        event_number_in_event_dict = 0
        event_dict = {}

        def append_to_event_dict(key, value):
            event_dict[key] = value

        for line in txt:
            line = line.decode("utf-8").rstrip("\r\n").strip()

            if line.startswith("</"):
                return

            elif line is None:
                continue

            elif "Category[:]" in line:
                last_string_name = 'Category'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "CategoryString[:]" in line:
                last_string_name = 'CategoryString'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "EventCode[:]" in line:
                last_string_name = 'EventCode'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "EventIdentifier[:]" in line:
                last_string_name = 'EventIdentifier'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "EventType[:]" in line:
                last_string_name = 'EventType'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "Logfile[:]" in line:
                last_string_name = 'Logfile'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "Message[:]" in line:
                last_string_name = 'Message'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "RecordNumber[:]" in line:
                last_string_name = 'RecordNumber'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "SourceName[:]" in line:
                last_string_name = 'SourceName'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "TimeGenerated[:]" in line:
                last_string_name = 'TimeGenerated'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "TimeWritten[:]" in line:
                last_string_name = 'TimeWritten'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "Type[:]" in line:
                last_string_name = 'Type'
                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())

            elif "User[:]" in line:
                last_string_name = 'User'

                append_to_event_dict(last_string_name, line.split("[:]")[1].strip())
                append_to_event_dict("Number", str(event_number_in_event_dict))

                self.result["NTLogEvent"].append(event_dict)

                event_number_in_event_dict += 1
                event_dict = {}

            else:
                if last_string_name == 'Message':
                    event_dict['Message'] += line + "\n"
                else:
                    event_dict[last_string_name] = line

    @staticmethod
    def open_gsi5txt_inside_gsi6zip(gsi6_file_name: str):
        r"""
        Принимает название файла GSI6.
        :return: IO[bytes]
            Возвращает текстовый файл GetSystemInfo...txt в формате списка.
        """
        gsi5_txt, net_diag, kl_version_hotfix, filter_manager = "", None, None, None
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

            for file in archive.namelist():

                if file.startswith("KL_Version_Hotfix"):
                    with archive.open(file) as txt:
                        kl_version_hotfix = txt.readlines()

                if file.startswith("Network_diagnostics"):
                    with archive.open(file) as txt:
                        net_diag = txt.readlines()

                if file.startswith("Filter_manager"):
                    with archive.open(file) as txt:
                        filter_manager = txt.readlines()

            return gsi5_txt, net_diag, kl_version_hotfix, filter_manager

    @staticmethod
    def open_gsi5txt(gsi_file_name: str) -> list[bytes]:
        with open(gsi_file_name, "rb") as txt:
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
                    return gsi_out, None, None, None
        elif gsi_file_name.endswith(".zip"):
            with ZipFile(gsi_file_name) as archive:
                if len(archive.namelist()) == 1 and archive.namelist()[0].startswith("GetSystemInfo"):
                    gsi_out = GetSystemInfoParser.open_gsi5zip(gsi_file_name)
                    return gsi_out, None, None, None
                else:
                    for name in archive.namelist():
                        if name.startswith("GetSystemInfo") and name.endswith(".zip"):
                            txt, net_diag, kl_version_hotfix, filter_manager = GetSystemInfoParser.open_gsi5txt_inside_gsi6zip(gsi_file_name)
                            return txt, net_diag, kl_version_hotfix, filter_manager
        return "Unknown", None, None, None

    @staticmethod
    def get_event_logs_from_gsi6(gsi6_file_name) -> tuple[list[dict] | None, list[dict] | None, list[dict] | None]:
        def evtx_to_dict(evt_bytes: bytes) -> list[dict]:
            num = 0
            parsed_records = []
            with BytesIO(evt_bytes) as evt:
                log_file = Evtx(evt)

                for record in log_file:
                    parsed_records.append({
                        "Num": num,
                        "Provider_Name": str(record.get("Provider_Name")),
                        "EventID": str(record.get("EventID")),
                        "Level": str(record.get("Level")),
                        "TimeCreated_SystemTime": str(record.get("TimeCreated_SystemTime")),
                        "EventRecordID": str(record.get("EventRecordID")),
                        "Channel": str(record.get("Channel")),
                        "Security_UserID": str(record.get("Security_UserID")),
                        "Data": str(record.get("Data")),
                    })
                    num += 1

            return parsed_records

        dict_kel, dict_sys, dict_app = None, None, None
        with ZipFile(gsi6_file_name) as archive:
            if "Eventlogs/Kaspersky Event Log.evt" in archive.namelist():
                try:
                    evt_kel = archive.read("Eventlogs/Kaspersky Event Log.evt")
                    dict_kel = evtx_to_dict(evt_kel)
                except:
                    pass

            # if "Eventlogs/System.evt" in archive.namelist():
            #     try:
            #         evt_sys = archive.read("Eventlogs/System.evt")
            #         dict_sys = evtx_to_dict(evt_sys)
            #     except:
            #         pass
            #
            # if "Eventlogs/Application.evt" in archive.namelist():
            #     try:
            #         evt_app = archive.read("Eventlogs/Application.evt")
            #         dict_app = evtx_to_dict(evt_app)
            #     except:
            #         pass

            return dict_kel, dict_sys, dict_app

if __name__ == "__main__":
    bigc = GetSystemInfoParser()
    reports_list = bigc.get_reports()
    print(f"\n\n{reports_list}")
    # txt, net_diag, kl_version_hotfix, filter_manager = bigc.get_information_from_gsi(reports_list[2])
    # bigc.main_reading_thread(txt, net_diag, kl_version_hotfix, filter_manager)
    bigc.get_event_logs_from_gsi6(reports_list[0])

