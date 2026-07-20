from textual.app import App, ComposeResult, Screen
from textual.widgets import Footer, Static, Input, OptionList, DataTable
from textual.containers import Vertical, Horizontal, Grid
from main import GetSystemInfoParser

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
        reports = self.app.GSI6.get_reports()
        with Vertical():
            preview = """┌――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――┐
▏              ▏                                                                                                                  ▏
▏  [lightgreen][blink].::   .::[/][/]   ▏    ██████╗ ███████╗████████╗███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗██╗███╗   ██╗███████╗ ██████╗   ▏
▏  [lightgreen][blink].::  .:: [/][/]   ▏   ██╔════╝ ██╔════╝╚══██╔══╝██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║██║████╗  ██║██╔════╝██╔═══██╗  ▏
▏  [lightgreen][blink].:: .::  [/][/]   ▏   ██║  ███╗█████╗     ██║   ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║██║██╔██╗ ██║█████╗  ██║   ██║  ▏
▏  [lightgreen][blink].: .:    [/][/]   ▏   ██║   ██║██╔══╝     ██║   ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ██║   ██║  ▏
▏  [lightgreen][blink].::  .:: [/][/]   ▏   ╚██████╔╝███████╗   ██║   ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║██║██║ ╚████║██║     ╚██████╔╝  ▏
▏  [lightgreen][blink].::   .:: [/][/]  ▏    ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝   ▏
▏              ▏                                                                                                [dim]by @Optionalles[/]   ▏
└――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――┘
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
            yield OptionList(
                *reports,
                id='menu',
            )
            yield Static(faq)
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.app.choosed_gsi_name = event.option.prompt
        txt, net_diag, evt_kel, evt_sys, evt_app = self.app.GSI6.get_information_from_gsi(self.app.choosed_gsi_name)
        self.app.GSI6.result = {}
        try:
            self.app.result = self.app.GSI6.main_reading_thread(txt, net_diag, evt_kel, evt_sys, evt_app)
        except:
            self.app.notify("The report is incorrect")
            return

        if self.app.result == "Unknown":
            self.app.notify("File don't recognized")
            return
        else:
            self.app.notify("Successfully")
            self.app.push_screen(GetSystemInfo())

    def action_refresh_page(self) -> None:
        option_list = self.query_one("#menu", OptionList)
        option_list.clear_options()
        for _ in self.app.GSI6.get_reports():
            option_list.add_option(_)
        self.notify("Refreshed!")



class GetSystemInfo(Screen):

    CSS = """
    OptionList {
        width: 22;
        height: 12;
        border: solid green;
        margin: 0 3 0 1;
    }
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
    .sttic {
        width: auto;
        height: auto;
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
        yield Static(f"┌────── GSI6 Menu ──────┐ ┌{(100 - len(self.app.choosed_gsi_name[:-4])) // 2 * "─"} {self.app.choosed_gsi_name[:-4]} {(100 - len(self.app.choosed_gsi_name[:-4])) // 2 * "─"}┐", classes="sttic")
        with Horizontal():
            yield OptionList("Kaspersky Info",
                             "System",
                             "Programs",
                             "Process",
                             "Services",
                             "Ports",
                             "Network",
                             "Events",
                             "KLnagchk",
                             "HOSTS",
                             )
            with Vertical():
                yield Static(id="text", classes="sttic")
                yield DataTable(id="table_programs", zebra_stripes=True)
                yield DataTable(id="table_process", zebra_stripes=True)
                yield DataTable(id="table_service", zebra_stripes=True)
                yield DataTable(id="table_ports", zebra_stripes=True)
                yield DataTable(id="table_gsi5_event_log", zebra_stripes=True)
                yield Input(placeholder="➤ Search...", id="search")
                yield Static(id="table_information", classes="table_information")


        # yield Static("└───────────────────────┘ └─────────────────────────────────────────────────────────────────┘")
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
            "[bold][green]Name[/][/]",
            "[bold][green]Version[/][/]",
        )

        table_process = self.query_one("#table_process", DataTable)
        table_process.display = False
        table_process.cursor_type = "row"
        table_process.add_column("[bold][green]Process[/][/]", width=34)
        table_process.add_column("[bold][green]Version[/][/]", width=15)
        table_process.add_column("[bold][green]FullName[/][/]", width=34)

        table_service = self.query_one("#table_service", DataTable)
        table_service.display = False
        table_service.cursor_type = "row"
        table_service.add_column("[bold][green]Process[/][/]", width=34)
        table_service.add_column("[bold][green]Version[/][/]", width=15)
        table_service.add_column("[bold][green]FullName[/][/]", width=34)
        table_service.add_column("[bold][green]State[/][/]", width=7)

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
        table_g5evl.add_column("[bold][green]Type[/][/]", width=15)
        table_g5evl.add_column("[bold][green]Time[/][/]", width=20)
        table_g5evl.add_column("[bold][green]Source[/][/]", width=40)
        table_g5evl.add_column("[bold][green]EvCode[/][/]", width=7)
        table_g5evl.add_column("[bold][green]From[/][/]", width=15)
        table_g5evl.add_column(label="[bold][green]User[/][/]", width=15)

        self.fill_static_kaspersky_info()
        self.fill_static_system_info()
        self.fill_table_programs(self.app.result["InstalledProduct"])
        self.fill_table_process(self.app.result["Process"])
        self.fill_table_service(self.app.result["Services"])
        self.fill_table_ports(self.app.result["OpenPorts"])
        self.fill_table_gsi5_event_log(self.app.result["NTLogEvent"])

    def fill_static_kaspersky_info(self):
        klproducts = ""

        for i in self.app.result["InstalledProduct"]:

            if "Kaspersky" in i or "Сервер администрирования" in i or "Агент администрирования" in i or "Плагин управления" in i:
                klproducts = klproducts + "▪ " + i + " (" + self.app.result["InstalledProduct"][i]["Version"] + ")" + "\n" + "                 "

            avstate = f""" [bold][lightgreen]ANTI-VIRUS STATISTIC (AVSTATE)[/][/]
 [dim]KSC Server:....[/] [lightyellow]{self.app.result["AVState"]["Protection_AdmServer"]}[/]
 [dim]Host ID:.......[/] {self.app.result["AVState"]["Protection_HostId"]}

 [dim]AV Installed:..[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_AvInstalled"] == "1" else "[red]NO[/]"}
 [dim]AV Running:....[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_AvRunning"] == "1" else "[red]NO[/]"}
 [dim]AV Bases Date:.[/] {self.app.result["AVState"]["Protection_BasesDate"]}
 [dim]Last Scan Date:[/] {self.app.result["AVState"]["Protection_LastFscan"]}
 [dim]Last Connect:..[/] {self.app.result["AVState"]["Protection_LastConnected"]}

 [dim]Dynamic VM:....[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_DynamicVM"] == "1" else "[red]NO[/]"}
 [dim]Ex Tenant ID:..[/] {self.app.result["AVState"]["Protection_ExternalTenantId"]}
"""
            self.app.text0 = f""" [bold][lightgreen]GENERAL INFORMATION[/][/]
 [dim]OS:............[/] {self.app.result["OperatingSystem"]["Caption"]} {self.app.result["OperatingSystem"]["Version"]}
 [dim]Processor:.....[/] {self.app.result["Processor"]["Name"]}
 [dim]GSI ver:.......[/] {self.app.result["gsi_ver"]}
 [dim]Memory:........[/] {str(int(self.app.result["OperatingSystem"]["TotalVisibleMemorySize"]) // 1000)} Mb
 [dim]KL Products:...[/] {klproducts}
\n""" + avstate

            # avstate = f"""▏[bold][lightgreen]ANTI-VIRUS STATISTIC (AVSTATE)[/]
# ▏[dim]KSC Server:....[/] {self.app.result["AVState"]["Protection_AdmServer"]}
# ▏[dim]Host ID:.......[/] {self.app.result["AVState"]["Protection_HostId"]}
# ▏――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
# ▏[dim]AV Installed:..[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_AvInstalled"] == "1" else "[red]NO[/]"}
# ▏[dim]AV Running:....[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_AvRunning"] == "1" else "[red]NO[/]"}
# ▏[dim]AV Bases Date:.[/] {self.app.result["AVState"]["Protection_BasesDate"]}
# ▏[dim]Last Scan Date:[/] {self.app.result["AVState"]["Protection_LastFscan"]}
# ▏[dim]Last Connect:..[/] {self.app.result["AVState"]["Protection_LastConnected"]}
# ▏――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
# ▏[dim]Dynamic VM:....[/] {"[green]YES[/]" if self.app.result["AVState"]["Protection_DynamicVM"] == "1" else "[red]NO[/]"}
# ▏[dim]Ex Tenant ID:..[/] {self.app.result["AVState"]["Protection_ExternalTenantId"]}
# └"""

            # self.app.text0 = f"""▏[bold]GENERAL INFORMATION[/]
# ▏[dim]OS:............[/] {self.app.result["OperatingSystem"]["Caption"]} {self.app.result["OperatingSystem"]["Version"]}
# ▏[dim]Processor:.....[/] {self.app.result["Processor"]["Name"]}
# ▏[dim]GSI ver:.......[/] {self.app.result["gsi_ver"]}
# ▏[dim]Memory:........[/] {str(int(self.app.result["OperatingSystem"]["TotalVisibleMemorySize"]) // 1000)} Mb
# ▏[dim]KL Products:...[/] {klproducts}
# ├――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――\n"""+avstate+"――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――"

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
            disks = disks + f''' ▪ ({self.app.result["LogicalDisk"][i]["DeviceID"]})      {self.app.result["LogicalDisk"][i]["Description"]}{psta1}{self.app.result["LogicalDisk"][i]["FileSystem"]}{psta2}{size} Gb{psta3}{freespace} Gb
 [lightskyblue]{size_bar}[/][dim]{"█████" * (10 - percentage)}[/]   [lightskyblue]{percentage * 10}%[/]\n
'''

        self.app.text1 = f""" [bold][lightgreen]COMPUTER[/][/]
 [dim]Processor:.....[/] {self.app.result["Processor"]["Name"]}
 [dim]Cores:.........[/] {str(int(self.app.result["Processor"]["DeviceID"].split("CPU")[1]) + 1) if self.app.result["Processor"]["SocketDesignation"].split()[0] == "CPU" else self.app.result["Processor"]["NumberOfCores"]} (Load {self.app.result["Processor"]["LoadPercentage"]}%)
 [dim]Manufacturer:..[/] {self.app.result["ComputerSystem"]["Manufacturer"]}
 [dim]Computer model:[/] {self.app.result["ComputerSystem"]["Model"]}
 [dim]System date:...[/] {self.app.result["Time"]["Time"]}

 [bold][lightgreen]BIOS[/][/]
 [dim]Name:..........[/] {self.app.result["BIOS"]["Name"]}
 [dim]Version:.......[/] {self.app.result["BIOS"]["Version"]}
 [dim]Date:..........[/] {self.app.result["BIOS"]["ReleaseDate"][0:4]}/{self.app.result["BIOS"]["ReleaseDate"][4:6]}/{self.app.result["BIOS"]["ReleaseDate"][6:8]}

 [bold][lightgreen]MISCELLANEOUS                              MEMORY[/][/]
 [dim]Procs count:...[/] {self.app.result["OperatingSystem"]["NumberOfProcesses"] + (" " * (27 - len(self.app.result["OperatingSystem"]["NumberOfProcesses"])))}[dim]Physic:....[/] {str(int(self.app.result["OperatingSystem"]["TotalVisibleMemorySize"]) // 1000)} Mb
 [dim]Users count:...[/] {self.app.result["OperatingSystem"]["NumberOfUsers"] + (" " * (27 - len(self.app.result["OperatingSystem"]["NumberOfUsers"])))}[dim]Available:.[/] {str(int(self.app.result["OperatingSystem"]["FreePhysicalMemory"]) // 1000)} Mb
 [dim]Architecture:..[/] {self.app.result["OperatingSystem"]["OSArchitecture"] + (" " * (27 - len(self.app.result["OperatingSystem"]["OSArchitecture"])))}[dim]Virtual:...[/] {str(int(self.app.result["OperatingSystem"]["TotalVirtualMemorySize"]) // 1000)} Mb
 [dim]Domain part:...[/] {self.app.result["ComputerSystem"]["PartOfDomain"] + (" " * (27 - len(self.app.result["ComputerSystem"]["PartOfDomain"])))}[dim]Available:.[/] {str(int(self.app.result["OperatingSystem"]["FreeVirtualMemory"]) // 1000)} Mb
 [dim]Domain:........[/] {self.app.result["ComputerSystem"]["Domain"]}
 [dim]Workgroup:.....[/] {self.app.result["ComputerSystem"]["Workgroup"]}
 [dim]Computer name:.[/] [lightyellow]{self.app.result["ComputerSystem"]["DNSHostName"]}[/]
 [dim]User name:.....[/] [lightyellow]{self.app.result["ComputerSystem"]["UserName"]}[/]
 [dim]System type:...[/] {self.app.result["ComputerSystem"]["SystemType"]}

 [bold]LOCAL DISKS STRUCTURE[/]
 [bold][dim]Disk name   Type                       File system   Total space   Free space[/][/]
""" + disks

    def fill_table_programs(self, result):
        table = self.query_one("#table_programs", DataTable)
        table.clear()
        for program in result:
            table.add_row(f"[bold]{program["Name"]}[/]",
                          program["Version"],
                          )

    def fill_table_process(self, result):
        table = self.query_one("#table_process", DataTable)
        table.clear()
        for process in result:
            table.add_row(f"[bold]{process["Process"]}[/]",
                          process["Version"],
                          process["FullName"],
                          )

    def fill_table_service(self, result):
        table = self.query_one("#table_service", DataTable)
        table.clear()
        for service in result:
            table.add_row(f"[bold]{service["Service"]}[/]",
                          service["Version"],
                          service["Name"],
                          F"[green]{service["State"]}[/]" if service["State"] == "Running" else f"[red]{service["State"]}[/]",
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
                          process["Status"],
                          )

    def fill_table_gsi5_event_log(self, result):
        table = self.query_one("#table_gsi5_event_log", DataTable)
        table.clear()
        for event in result:
            timestamp = f"{event["Time"].split(".")[0][:4]}/{event["Time"].split(".")[0][4:6]}/{event["Time"].split(".")[0][6:8]} {event["Time"].split(".")[0][8:10]}:{event["Time"].split(".")[0][10:12]}:{event["Time"].split(".")[0][12:14]}"
            table.add_row(f"[bold]{event["Type"]}[/]",
                          timestamp,
                          event["Source_name"],
                          event["Event_code"],
                          event["Log_file"],
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
                        or text in port["Time"]
                        or text in port["Source_name"]
                        or text in port["Event_code"]
                        or text in port["Log_file"]
                        or text in port["User"].lower()
                        or text in port["Message"].lower()
                ):
                    filtered.append(port)
            self.fill_table_gsi5_event_log(filtered)

    def on_data_table_row_highlighted(self, event: DataTable.RowSelected):
        self.query_one("#table_information", Static).update(f"""
[bold][lightgreen]Message:[/][/] {self.app.result["NTLogEvent"][event.cursor_row]["Message"]}
[bold][lightgreen]Source:[/][/] {self.app.result["NTLogEvent"][event.cursor_row]["Source_name"]}
[bold][lightgreen]From:[/][/] {self.app.result["NTLogEvent"][event.cursor_row]["Log_file"]}
[bold][lightgreen]User:[/][/] {self.app.result["NTLogEvent"][event.cursor_row]["User"]}
""")

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self.query_one("#text", Static).display = False
        self.query_one("#table_programs", DataTable).display = False
        self.query_one("#table_process", DataTable).display = False
        self.query_one("#table_service", DataTable).display = False
        self.query_one("#table_ports", DataTable).display = False
        self.query_one("#table_gsi5_event_log", DataTable).display = False
        self.query_one("#search", Input).display = False
        self.query_one("#search", Input).clear()
        self.query_one("#table_information", Static).display = False

        selected = event.option.prompt

        if selected == "Kaspersky Info":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.text0)

        elif selected == "System":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.text1)

        elif selected == "Programs":
            self.query_one("#table_programs", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.app.input_flag = "Programs"

        elif selected == "Process":
            self.query_one("#table_process", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.app.input_flag = "Process"

        elif selected == "Services":
            self.query_one("#table_service", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.app.input_flag = "Services"

        elif selected == "Ports":
            self.query_one("#table_ports", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.app.input_flag = "Ports"

        elif selected == "Network":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.result["net_diag"])

        elif selected == "Events":
            self.query_one("#table_gsi5_event_log", DataTable).display = True
            self.query_one("#search", Input).display = True
            self.query_one("#table_information", Static).display = True
            self.app.input_flag = "Events"

        elif selected == "KLnagchk":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.result["Network_Agent_report"])

        elif selected == "HOSTS":
            self.query_one("#text", Static).display = True
            self.query_one("#text", Static).update(self.app.result["HOSTS"])


    def action_back(self):
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
        self.GSI6 = GetSystemInfoParser()
        self.choosed_gsi_name = ""
        self.result = {}
        self.list_of_gsi_names = []
        self.input_flag = ""
        self.text0 = ""
        self.text1 = ""
        self.text2 = ""

    def on_mount(self):
        self.push_screen(ChooseGSI())










if __name__ == "__main__":
    GetSystemInfoUtilityParser().run()