
from concurrent.futures import ProcessPoolExecutor
from textual.app import App, ComposeResult, Screen
from textual.widgets import Footer, Static, Input, OptionList, DataTable, Button
from textual.containers import Vertical, Horizontal
from textual import work
from parser import GetSystemInfoParser

executor = ProcessPoolExecutor(max_workers=1)

class ChooseGSI(Screen):

    CSS = """
    Vertical {
        align-horizontal: center;
    }
    
    OptionList {
        width: 128;
    }
    
    Static {
        width: auto;
    }
    """

    BINDINGS = [
        ("ctrl+r", "refresh_page", "Refresh"),
        ]

    def compose(self) -> ComposeResult:
        with Vertical():
            preview = """┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃              ┃                                                                                                                 ┃
┃  [lightgreen][blink].::   .::[/][/]   ┃    ██████╗ ███████╗████████╗███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗██╗███╗   ██╗███████╗ ██████╗  ┃
┃  [lightgreen][blink].::  .:: [/][/]   ┃   ██╔════╝ ██╔════╝╚══██╔══╝██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║██║████╗  ██║██╔════╝██╔═══██╗ ┃
┃  [lightgreen][blink].:: .::  [/][/]   ┃   ██║  ███╗█████╗     ██║   ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║██║██╔██╗ ██║█████╗  ██║   ██║ ┃
┃  [lightgreen][blink].: .:    [/][/]   ┃   ██║   ██║██╔══╝     ██║   ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ██║   ██║ ┃
┃  [lightgreen][blink].::  .:: [/][/]   ┃   ╚██████╔╝███████╗   ██║   ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║██║██║ ╚████║██║     ╚██████╔╝ ┃
┃  [lightgreen][blink].::   .:: [/][/]  ┃    ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝  ┃
┃              ┃                                                                                                [dim]by @Optionalles[/]  ┃
┗━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

            faq = """
[bold][lightgreen]CONTROL                                                            УПРАВЛЕНИЕ[/]
⬆ - up;                                                            ⬆ - вверх;
⬇ - down                                                           ⬇ - вниз
Enter - select;                                                    Enter - выбрать;
Mouse selection is available;                                      Выбор мышью - доступен;
  
Ctrl+R - refresh the report selection page.                        Ctrl+R - обновить страницу с выбором отчетов. 
Useful when adding a new .zip report to the utility directory.     Полезно при добавлении нового .zip-отчета в каталог с утилитой.
Allows you to avoid the need to restart the utility.               Позволяет избежать необходимости перезагрузки утилиты.

Ctrl+B - go back;                                                  Ctrl+B - вернуться назад;

Ctrl+Q - exit the utility;                                         Ctrl+Q - выйти из утилиты;

If you want to change the size of the text and the script          Если Вы хотите изменить размер текста и в целом,
interface in general, please use [Ctrl+Mouse Wheel]                интерфейса скрипта, пожалуйста, перед запуском утилиты
before launching the utility.                                      используйте зажатый [Ctrl+Колесико мыши].
"""
            yield Static(preview)
            yield OptionList(id='menu')
            yield Static(faq)
        yield Footer()

    @work(thread=True)
    def get_logs_from_evtx_worker(self, gsi6_file_name):
        parser = GetSystemInfoParser().get_event_logs_from_gsi6
        future = executor.submit(parser, gsi6_file_name)
        self.notify("JOB: GSI6 .evt parsing...")
        self.app.dict_kel, self.app.dict_sys, self.app.dict_app = future.result()
        self.notify("JOB: GSI6 .evt parsing ended!")

    def on_mount(self):
        reports = GetSystemInfoParser().get_reports()
        for report in reports:
            self.query_one("#menu", OptionList).add_option(report)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.app.choosed_gsi_name = event.option.prompt

        try:
            txt, net_diag, kl_version_hotfix, filter_manager = GetSystemInfoParser().get_information_from_gsi(self.app.choosed_gsi_name)
        except FileNotFoundError as e:
            self.app.notify("The file does not exist")
            return

        try:
            self.app.result = GetSystemInfoParser().main_reading_thread(txt, net_diag, kl_version_hotfix, filter_manager)
        except:
            self.app.notify("The report is incorrect")
            return

        if self.app.result == "Unknown":
            self.app.notify("File don't recognized")
            return
        else:
            self.app.notify("Successfully")
            self.get_logs_from_evtx_worker(self.app.choosed_gsi_name)
            self.app.push_screen(GetSystemInfo())

    def action_refresh_page(self) -> None:
        option_list = self.query_one("#menu", OptionList)
        option_list.clear_options()
        for _ in GetSystemInfoParser().get_reports():
            option_list.add_option(_)
        self.notify("Refreshed!")




class GetSystemInfo(Screen):

    CSS = """
    Horizontal {
        width: auto;
        height: auto;
    }
    Vertical {
        width: auto;
        height: auto;
    }
    DataTable {
        width: 100;
        height: 15;
        margin: 0 0 0 1;
    }
    .optional_menu {
        width: 22;
        height: 14;
        border: solid green;
        margin: 0 3 0 1;
    }
    .optional_event_logs {
        width: 22;
        height: 6;
        border: solid green;
        margin: 0 3 0 1;
    }
    .sttic {
        width: auto;
        height: auto;
    }
    .button {
        width: 22;
        height: 3;
        border: solid green;
        margin: 0 3 0 1;
    }
    .table_information {
        width: 100;
        height: auto;
        margin: 0 0 0 1;
    }
    #details {
        grid-size: 1;
        grid-columns: auto 1fr;
    }
    """

    BINDINGS = [
        ("ctrl+b", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(f"┏━━━━━━ GSI6 Menu ━━━━━━┓ ┏{(100 - len(self.app.choosed_gsi_name[:-4])) // 2 * "━"} {self.app.choosed_gsi_name[:-4]} {(100 - len(self.app.choosed_gsi_name[:-4])) // 2 * "━"}┓", classes="sttic")
        with Horizontal():
            with Vertical():
                yield OptionList("✦ About Kaspersky",
                                 "✦ System",
                                 "✦ Programs",
                                 "✦ Process",
                                 "✦ Services",
                                 "✦ Drivers",
                                 "✦ Ports",
                                 "✦ Events (GSI5)",
                                 "✦ Network",
                                 "✦ Filter Manager",
                                 "✦ Klnagchk",
                                 "✦ Hosts",
                                 classes="optional_menu")
                yield Static(f"┏━━━━━━ Eventlogs ━━━━━━┓", classes="sttic")
                # yield OptionList("✦ Kaspersky\n  Event Logs",
                #                  "✦ Application Logs",
                #                  "✦ System Logs",
                #                  classes="optional_event_logs")
                yield Button(label="Kaspersky Events", name="Kaspersky Event Logs", classes="button")
                yield Button(label="Application", name="Application123", classes="button")
                yield Button(label="System", name="System", classes="button")
            with Vertical():
                yield Static(id="text", classes="sttic")
                yield DataTable(id="table_programs", zebra_stripes=True)
                yield DataTable(id="table_process", zebra_stripes=True)
                yield DataTable(id="table_service", zebra_stripes=True)
                yield DataTable(id="table_drivers", zebra_stripes=True)
                yield DataTable(id="table_ports", zebra_stripes=True)
                yield DataTable(id="table_gsi5_event_log", zebra_stripes=True)
                yield Input(placeholder="➤ Search...", id="search")
                yield Static(id="table_information", classes="table_information")
                yield Static(id="table_information_programs", classes="table_information")
                yield Static(id="table_information_process", classes="table_information")
                yield Static(id="table_information_services", classes="table_information")
                yield Static(id="table_information_drivers", classes="table_information")

        yield Footer()

    def on_mount(self):
        static = self.query_one("#text", Static)
        static.display = False

        search = self.query_one("#search", Input)
        search.display = False

        table_programs = self.query_one("#table_programs", DataTable)
        table_programs.display = False
        table_programs.cursor_type = "row"
        table_programs.add_columns(
            "[bold][green]Num[/][/]",
            "[bold][green]Name[/][/]",
            "[bold][green]Version[/][/]",
        )

        table_process = self.query_one("#table_process", DataTable)
        table_process.display = False
        table_process.cursor_type = "row"
        table_process.add_column("[bold][green]Num[/][/]", width=5)
        table_process.add_column("[bold][green]Process[/][/]", width=32)
        table_process.add_column("[bold][green]Version[/][/]", width=15)
        table_process.add_column("[bold][green]FullName[/][/]", width=31)

        table_service = self.query_one("#table_service", DataTable)
        table_service.display = False
        table_service.cursor_type = "row"
        table_service.add_column("[bold][green]Num[/][/]", width=5)
        table_service.add_column("[bold][green]Process[/][/]", width=31)
        table_service.add_column("[bold][green]Version[/][/]", width=15)
        table_service.add_column("[bold][green]FullName[/][/]", width=30)
        table_service.add_column("[bold][green]State[/][/]", width=7)

        table_drivers = self.query_one("#table_drivers", DataTable)
        table_drivers.display = False
        table_drivers.cursor_type = "row"
        table_drivers.add_column("[bold][green]Num[/][/]", width=5)
        table_drivers.add_column("[bold][green]Driver[/][/]", width=31)
        table_drivers.add_column("[bold][green]Description[/][/]", width=30)
        table_drivers.add_column("[bold][green]StartMode[/][/]", width=15)
        table_drivers.add_column("[bold][green]State[/][/]", width=7)

        table_ports = self.query_one("#table_ports", DataTable)
        table_ports.display = False
        table_ports.cursor_type = "row"
        table_ports.add_columns(
            "[bold][green]Prtcl[/][/]",
            "[bold][green]Process[/][/]",
            "[bold][green]Src IP[/][/]",
            "[bold][green]Src Port[/][/]",
            "[bold][green]Dest IP[/][/]",
            "[bold][green]Dest Port[/][/]",
            "[bold][green]Status[/][/]",
        )

        table_g5evl = self.query_one("#table_gsi5_event_log", DataTable)
        table_g5evl.display = False
        table_g5evl.cursor_type = "row"
        table_g5evl.add_column("[bold][green]Num[/][/]", width=5)
        table_g5evl.add_column("[bold][green]Type[/][/]", width=15)
        table_g5evl.add_column("[bold][green]Time[/][/]", width=20)
        table_g5evl.add_column("[bold][green]Source[/][/]", width=30)
        table_g5evl.add_column("[bold][green]EvCode[/][/]", width=7)
        table_g5evl.add_column("[bold][green]From[/][/]", width=15)
        table_g5evl.add_column(label="[bold][green]User[/][/]", width=15)

        self.fill_static_kaspersky_info()
        self.fill_static_system_info()
        self.fill_table_programs(self.app.result["InstalledProduct"])
        self.fill_table_process(self.app.result["Process"])
        self.fill_table_service(self.app.result["Services"])
        self.fill_table_drivers(self.app.result["SystemDriver"])
        self.fill_table_ports(self.app.result["OpenPorts"])
        self.fill_table_gsi5_event_log(self.app.result["NTLogEvent"])

        self.app.total_events_count = len(self.app.result["NTLogEvent"])

    def fill_static_kaspersky_info(self):
        klproducts = ""

        for i in self.app.result["InstalledProduct"]:

            if ("Kaspersky" in i["Name"] or "Сервер администрирования" in i["Name"] or "Агент администрирования" in i["Name"] or "Плагин управления" in i["Name"]) and f"{i["Name"] + " (" + i["Version"] + ")"}" not in klproducts:
                klproducts = klproducts + "▪ " + i["Name"] + " (" + i["Version"] + ")" + "\n" + "┃                 "

        self.app.avstate = f"""┃ [bold][lightgreen]ANTI-VIRUS STATISTIC (AVSTATE)[/][/]
┃ [dim]KSC Server:....[/] {self.app.result["AVState"]["Protection_AdmServer"]}
┃ [dim]Host ID:.......[/] {self.app.result["AVState"]["Protection_HostId"]}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ [dim]AV Patches:....[/] {self.app.result["KL_Version_Hotfix"]}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ [dim]AV Installed:..[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_AvInstalled"] == "1" else "[red]NO[/]"}
┃ [dim]AV Running:....[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_AvRunning"] == "1" else "[red]NO[/]"}
┃ [dim]AV Bases Date:.[/] {self.app.result["AVState"]["Protection_BasesDate"]}
┃ [dim]Last Scan Date:[/] {self.app.result["AVState"]["Protection_LastFscan"]}
┃ [dim]Last Connect:..[/] {self.app.result["AVState"]["Protection_LastConnected"]}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ [dim]Dynamic VM:....[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_DynamicVM"] == "1" else "[red]NO[/]"}
┃ [dim]Ex Tenant ID:..[/] {self.app.result["AVState"]["Protection_ExternalTenantId"]}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        self.app.text0 = f"""┃ [bold][lightgreen]GENERAL INFORMATION[/][/]
┃ [dim]OS:............[/] {self.app.result["OperatingSystem"]["Caption"]} ({self.app.result["OperatingSystem"]["Version"]})
┃ [dim]Processor:.....[/] {self.app.result["Processor"]["Name"]}
┃ [dim]GSI ver:.......[/] {self.app.result["gsi_ver"]}
┃ [dim]Memory:........[/] {str(int(self.app.result["OperatingSystem"]["TotalVisibleMemorySize"]) // 1000)} Mb
┃ [dim]KL Products:...[/] {klproducts}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n""" + self.app.avstate

    def fill_static_system_info(self):
        disks = ""

        for i in self.app.result["LogicalDisk"]:
            size_bar = '█████'
            psta1, psta2, psta3 = "", "", ""
            ldlen1 = int(len(self.app.result["LogicalDisk"][i]["Description"]))
            ldlen2 = int(len(self.app.result["LogicalDisk"][i]["FileSystem"]))
            ldlen3 = int(len(self.app.result["LogicalDisk"][i]["FreeSpace"]))
            if ldlen1 < 27:
                for _ in range(27 - ldlen1):
                    psta1 = psta1 + " "
            if ldlen2 < 14:
                for _ in range(14 - ldlen2):
                    psta2 = psta2 + " "
            if ldlen3 < 14:
                for _ in range(10 - ldlen2):
                    psta3 = psta3 + " "
                    size = ("0" if self.app.result["LogicalDisk"][i]["Size"] == '' else str(((int(self.app.result["LogicalDisk"][i]["Size"]) / 1024) / 1024) / 1024)[:5])
                    freespace = ("0" if self.app.result["LogicalDisk"][i]["FreeSpace"] == '' else str(((int(self.app.result["LogicalDisk"][i]["FreeSpace"]) / 1024) / 1024) / 1024)[:6])
            try:
                percentage = int(((int(size.split(".")[0]) - int(freespace.split(".")[0])) // (int(size.split(".")[0]) / 100))) // 10
            except:
                percentage = 0
            size_bar = size_bar * percentage
            disks = disks + f'''┃ ▪ ({self.app.result["LogicalDisk"][i]["DeviceID"]})      {self.app.result["LogicalDisk"][i]["Description"]}{psta1}{self.app.result["LogicalDisk"][i]["FileSystem"]}{psta2}{size} Gb{psta3}{freespace} Gb
┃ [lightskyblue]{size_bar}[/][dim]{"█████" * (10 - percentage)}[/]   [lightskyblue]{percentage * 10}%[/]\n┃
'''

        self.app.text1 = f"""┃ [bold][lightgreen]COMPUTER[/][/]
┃ [dim]Processor:.....[/] {self.app.result["Processor"]["Name"]}
┃ [dim]Cores:.........[/] {str(int(self.app.result["Processor"]["DeviceID"].split("CPU")[1]) + 1) if self.app.result["Processor"]["SocketDesignation"].split()[0] == "CPU" else self.app.result["Processor"]["NumberOfCores"]} (Load {self.app.result["Processor"]["LoadPercentage"]}%)
┃ [dim]Manufacturer:..[/] {self.app.result["ComputerSystem"]["Manufacturer"]}
┃ [dim]Computer model:[/] {self.app.result["ComputerSystem"]["Model"]}
┃ [dim]System date:...[/] {self.app.result["Time"]["Time"]}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ [bold][lightgreen]BIOS[/][/]
┃ [dim]Name:..........[/] {self.app.result["BIOS"]["Name"]}
┃ [dim]Version:.......[/] {self.app.result["BIOS"]["Version"]}
┃ [dim]Date:..........[/] {self.app.result["BIOS"]["ReleaseDate"][0:4]}/{self.app.result["BIOS"]["ReleaseDate"][4:6]}/{self.app.result["BIOS"]["ReleaseDate"][6:8]}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ [bold][lightgreen]MISCELLANEOUS                              MEMORY[/][/]
┃ [dim]Procs count:...[/] {self.app.result["OperatingSystem"]["NumberOfProcesses"] + (" " * (27 - len(self.app.result["OperatingSystem"]["NumberOfProcesses"])))}[dim]Physic:....[/] {str(int(self.app.result["OperatingSystem"]["TotalVisibleMemorySize"]) // 1000)} Mb
┃ [dim]Users count:...[/] {self.app.result["OperatingSystem"]["NumberOfUsers"] + (" " * (27 - len(self.app.result["OperatingSystem"]["NumberOfUsers"])))}[dim]Available:.[/] {str(int(self.app.result["OperatingSystem"]["FreePhysicalMemory"]) // 1000)} Mb
┃ [dim]Architecture:..[/] {self.app.result["OperatingSystem"]["OSArchitecture"] + (" " * (27 - len(self.app.result["OperatingSystem"]["OSArchitecture"])))}[dim]Virtual:...[/] {str(int(self.app.result["OperatingSystem"]["TotalVirtualMemorySize"]) // 1000)} Mb
┃ [dim]Domain part:...[/] {self.app.result["ComputerSystem"]["PartOfDomain"] + (" " * (27 - len(self.app.result["ComputerSystem"]["PartOfDomain"])))}[dim]Available:.[/] {str(int(self.app.result["OperatingSystem"]["FreeVirtualMemory"]) // 1000)} Mb
┃ [dim]Domain:........[/] {self.app.result["ComputerSystem"]["Domain"]}
┃ [dim]Workgroup:.....[/] {self.app.result["ComputerSystem"]["Workgroup"]}
┃ [dim]Computer name:.[/] [lightyellow]{self.app.result["ComputerSystem"]["DNSHostName"]}[/]
┃ [dim]User name:.....[/] [lightyellow]{self.app.result["ComputerSystem"]["UserName"]}[/]
┃ [dim]System type:...[/] {self.app.result["ComputerSystem"]["SystemType"]}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ [bold][lightgreen]LOCAL DISKS STRUCTURE[/][/]
┃ [bold][dim]Disk name   Type                       File system   Total space   Free space[/][/]
""" + disks + "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"

    def fill_table_programs(self, result):
        table = self.query_one("#table_programs", DataTable)
        table.clear()
        for program in result:
            table.add_row(program["Num"],
                          f"[bold]{program["Name"]}[/]",
                          program["Version"],
                          )

    def fill_table_process(self, result):
        table = self.query_one("#table_process", DataTable)
        table.clear()
        for process in result:
            table.add_row(process["Num"],
                          f"[bold]{process["Process"]}[/]",
                          process["Version"],
                          process["FullName"],
                          )

    def fill_table_service(self, result):
        table = self.query_one("#table_service", DataTable)
        table.clear()
        for service in result:
            table.add_row(service["Num"],
                          f"[bold]{service["Service"]}[/]",
                          service["Version"],
                          service["Name"],
                          F"[green]{service["State"]}[/]" if service["State"] == "Running" else f"[red]{service["State"]}[/]",
                          )

    def fill_table_drivers(self, result):
        table = self.query_one("#table_drivers", DataTable)
        table.clear()
        for driver in result:
            table.add_row(driver["Num"],
                          f"[bold]{driver["Name"]}[/]",
                          driver["Description"],
                          driver["StartMode"],
                          F"[green]{driver["State"]}[/]" if driver["State"] == "Running" else f"[red]{driver["State"]}[/]",
                          )

    def fill_table_ports(self, result):
        table = self.query_one("#table_ports", DataTable)
        table.clear()
        for process in result:
            table.add_row(process["Protocol"],
                          process["Process"],
                          process["Source_ip"],
                          process["Source_port"],
                          process["Destination_ip"],
                          process["Destination_port"],
                          f"""{f"[blue]{process["Status"]}[/]" if process["Status"] == "LISTEN" else (f"[green]{process["Status"]}[/]" if process["Status"] == "ESTAB" else f"[yellow]{process["Status"]}[/]")}""",
                          )

    def fill_table_gsi5_event_log(self, result):
        table = self.query_one("#table_gsi5_event_log", DataTable)
        table.clear()
        for event in result:
            timestamp = f"{event["TimeGenerated"].split(".")[0][:4]}/{event["TimeGenerated"].split(".")[0][4:6]}/{event["TimeGenerated"].split(".")[0][6:8]} {event["TimeGenerated"].split(".")[0][8:10]}:{event["TimeGenerated"].split(".")[0][10:12]}:{event["TimeGenerated"].split(".")[0][12:14]}"
            table.add_row(event["Number"],
                    f"[bold]{event["Type"]}[/]",
                          timestamp,
                          event["SourceName"],
                          event["EventCode"],
                          event["Logfile"],
                          event["User"],
                          )

    def on_input_changed(self, event: Input.Changed):
        text = event.value.lower()
        filtered = []

        if self.app.input_flag == "Programs":
            for port in self.app.result["InstalledProduct"]:

                if (
                        text in port["Name"].lower()
                        or text in port["Version"]
                ):
                    filtered.append(port)
            self.fill_table_programs(filtered)

        if self.app.input_flag == "Process":
            for port in self.app.result["Process"]:

                if (
                        text in port["Process"].lower()
                        or text in port["Version"]
                        or text in port["FullName"].lower()
                ):
                    filtered.append(port)
            self.fill_table_process(filtered)

        if self.app.input_flag == "Services":
            for port in self.app.result["Services"]:

                if (
                        text in port["Service"].lower()
                        or text in port["Version"]
                        or text in port["Name"].lower()
                        or text in port["State"].lower()
                ):
                    filtered.append(port)
            self.fill_table_service(filtered)

        if self.app.input_flag == "Drivers":
            for port in self.app.result["SystemDriver"]:

                if (
                        text in port["Name"].lower()
                        or text in port["Description"]
                        or text in port["StartMode"].lower()
                        or text in port["State"].lower()
                ):
                    filtered.append(port)
            self.fill_table_drivers(filtered)

        if self.app.input_flag == "Ports":
            for port in self.app.result["OpenPorts"]:

                if (
                        text in port["Process"].lower()
                        or text in port["Source_port"]
                        or text in port["Destination_port"]
                        or text in port["Source_ip"]
                        or text in port["Destination_ip"]
                        or text in port["Protocol"].lower()
                        or text in port["Status"].lower()
                ):
                    filtered.append(port)
            self.fill_table_ports(filtered)

        if self.app.input_flag == "Events":
            for port in self.app.result["NTLogEvent"]:

                if (
                        text in port["Type"].lower()
                        or text in port["TimeGenerated"]
                        or text in port["SourceName"].lower()
                        or text in port["EventCode"]
                        or text in port["Logfile"].lower()
                        or text in port["User"].lower()
                        or text in port["Message"].lower()
                ):
                    filtered.append(port)
            self.fill_table_gsi5_event_log(filtered)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        try:
            if "table_gsi5_event_log" == event.data_table.id:
                row_num = int(event.data_table.get_row(event.row_key)[0])
                self.query_one("#table_information", Static).update(f"""
[bold][dim]Message:[/][/] {self.app.result["NTLogEvent"][row_num]["Message"]}
[bold][dim]Source:.[/][/] {self.app.result["NTLogEvent"][row_num]["SourceName"]}
[bold][dim]From:...[/][/] {self.app.result["NTLogEvent"][row_num]["Logfile"]}
[bold][dim]User:...[/][/] [lightyellow]{self.app.result["NTLogEvent"][row_num]["User"]}[/]
    
[bold][dim]Total Events Count:[/][/] {self.app.total_events_count}
    
[red][bold]Annotation[/][/]
This Events parsed from GSI5.
Usually there are event logs only for the last 3 days
 """)

            if "table_programs" == event.data_table.id:
                row_num = int(event.data_table.get_row(event.row_key)[0])
                self.query_one("#table_information_programs", Static).update(f"""
[bold][dim]Name:............[/][/] {self.app.result["InstalledProduct"][row_num]["Name"]}
[bold][dim]Uninstall:.......[/][/] {self.app.result["InstalledProduct"][row_num]["Uninstall"]}
[bold][dim]Vendor:..........[/][/] {self.app.result["InstalledProduct"][row_num]["Vendor"]}
[bold][dim]Version:.........[/][/] {self.app.result["InstalledProduct"][row_num]["Version"]}
[bold][dim]InstallDate:.....[/][/] {self.app.result["InstalledProduct"][row_num]["InstallDate"]}
[bold][dim]InstallLocation:.[/][/] {self.app.result["InstalledProduct"][row_num]["InstallLocation"]}
[bold][dim]Language:........[/][/] {self.app.result["InstalledProduct"][row_num]["Language"]}
 """)

            if "table_process" == event.data_table.id:
                row_num = int(event.data_table.get_row(event.row_key)[0])
                self.query_one("#table_information_process", Static).update(f"""
[bold][dim]Process:.....[/][/] {self.app.result["Process"][row_num]["Process"]}
[bold][dim]Version_dev:.[/][/] {self.app.result["Process"][row_num]["Version_dev"]}
[bold][dim]Version:.....[/][/] {self.app.result["Process"][row_num]["Version"]}
[bold][dim]FullName:....[/][/] {self.app.result["Process"][row_num]["FullName"]}
 """)

            if "table_service" == event.data_table.id:
                row_num = int(event.data_table.get_row(event.row_key)[0])
                self.query_one("#table_information_services", Static).update(f"""
[bold][dim]Service:.....[/][/] {self.app.result["Services"][row_num]["Service"]}
[bold][dim]Version_dev:.[/][/] {self.app.result["Services"][row_num]["Version_dev"]}
[bold][dim]Version:.....[/][/] {self.app.result["Services"][row_num]["Version"]}
[bold][dim]FullName:....[/][/] {self.app.result["Services"][row_num]["FullName"]}
[bold][dim]Pathname:....[/][/] {self.app.result["Services"][row_num]["Pathname"]}
[bold][dim]Name:........[/][/] {self.app.result["Services"][row_num]["Name"]}
[bold][dim]ServiceType:.[/][/] {self.app.result["Services"][row_num]["ServiceType"]}
[bold][dim]ProcessID:...[/][/] {self.app.result["Services"][row_num]["ProcessID"]}
[bold][dim]Description:.[/][/] {self.app.result["Services"][row_num]["Description"]}
[bold][dim]DisplayName:.[/][/] {self.app.result["Services"][row_num]["DisplayName"]}
[bold][dim]Started:.....[/][/] {self.app.result["Services"][row_num]["Started"]}
[bold][dim]StartMode:...[/][/] {self.app.result["Services"][row_num]["StartMode"]}
[bold][dim]State:.......[/][/] {self.app.result["Services"][row_num]["State"]}
[bold][dim]Status:......[/][/] {self.app.result["Services"][row_num]["Status"]}
 """)

            if "table_drivers" == event.data_table.id:
                row_num = int(event.data_table.get_row(event.row_key)[0])
                self.query_one("#table_information_drivers", Static).update(f"""
[bold][dim]Driver:......[/][/] {self.app.result["SystemDriver"][row_num]["Name"]}
[bold][dim]Caption:.....[/][/] {self.app.result["SystemDriver"][row_num]["Caption"]}
[bold][dim]Description:.[/][/] {self.app.result["SystemDriver"][row_num]["Description"]}
[bold][dim]Pathname:....[/][/] {self.app.result["SystemDriver"][row_num]["PathName"]}
[bold][dim]ServiceType:.[/][/] {self.app.result["SystemDriver"][row_num]["ServiceType"]}
[bold][dim]Started:.....[/][/] {self.app.result["SystemDriver"][row_num]["Started"]}
[bold][dim]StartMode:...[/][/] {self.app.result["SystemDriver"][row_num]["StartMode"]}
[bold][dim]State:.......[/][/] {self.app.result["SystemDriver"][row_num]["State"]}
[bold][dim]Status:......[/][/] {self.app.result["SystemDriver"][row_num]["Status"]}
         """)

        except Exception as e:
            pass

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self.query_one("#text", Static).display = False
        self.query_one("#table_programs", DataTable).display = False
        self.query_one("#table_process", DataTable).display = False
        self.query_one("#table_service", DataTable).display = False
        self.query_one("#table_drivers", DataTable).display = False
        self.query_one("#table_ports", DataTable).display = False
        self.query_one("#table_gsi5_event_log", DataTable).display = False
        self.query_one("#search", Input).display = False
        self.query_one("#search", Input).clear()
        self.query_one("#table_information", Static).display = False
        self.query_one("#table_information_programs", Static).display = False
        self.query_one("#table_information_process", Static).display = False
        self.query_one("#table_information_services", Static).display = False
        self.query_one("#table_information_drivers", Static).display = False

        selected = event.option.prompt

        if selected == "✦ About Kaspersky":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.text0)

        elif selected == "✦ System":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.text1)

        elif selected == "✦ Programs":
            self.query_one("#table_programs", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.query_one("#table_information_programs", Static).display = True
            self.app.input_flag = "Programs"

        elif selected == "✦ Process":
            self.query_one("#table_process", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.query_one("#table_information_process", Static).display = True
            self.app.input_flag = "Process"

        elif selected == "✦ Services":
            self.query_one("#table_service", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.query_one("#table_information_services", Static).display = True
            self.app.input_flag = "Services"

        elif selected == "✦ Drivers":
            self.query_one("#table_drivers", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.query_one("#table_information_drivers", Static).display = True
            self.app.input_flag = "Drivers"

        elif selected == "✦ Ports":
            self.query_one("#table_ports", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.app.input_flag = "Ports"

        elif selected == "✦ Network":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.result["net_diag"])

        elif selected == "✦ Filter Manager":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.result["filter_manager"])

        elif selected == "✦ Events (GSI5)":
            self.query_one("#table_gsi5_event_log", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.query_one("#table_information", Static).display = True
            self.app.input_flag = "Events"

        elif selected == "✦ Klnagchk":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.result["Network_Agent_report"])

        elif selected == "✦ Hosts":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.result["HOSTS"])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_name = event.button.name
        static = self.query_one("#text", Static)
        try:
            static.update(str(self.app.dict_kel[0]))
        except Exception as e:
            event.button.action_notify(str(e))

    def action_back(self):
        self.app.result = {}
        self.app.pop_screen()


class GetSystemInfoUtilityParser(App):

    CSS = """
    OptionList {
        width: 70;
        border: solid green;
        margin: 0 1 0 1;
    }
    RichLog {
        width: 70;
        border: solid green;
        margin: 0 1 0 1;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.choosed_gsi_name = ""
        self.result = {}
        self.list_of_gsi_names = []
        self.input_flag = ""
        self.text0 = ""
        self.text1 = ""
        self.text2 = ""
        self.avstate = ""
        self.total_events_count = 0
        self.app.dict_kel = None

    def on_mount(self):
        self.push_screen(ChooseGSI())










if __name__ == "__main__":
    GetSystemInfoUtilityParser().run()