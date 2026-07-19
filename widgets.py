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
        txt, net_diag = self.app.GSI6.get_information_from_gsi(self.app.choosed_gsi_name)
        self.app.GSI6.result = {}
        try:
            self.app.result = self.app.GSI6.main_reading_thread(txt, net_diag)
        except KeyError:
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
        height: 11;
        border: solid green;
        margin: 0 3 0 1;
    }
    Horizontal {
        width: auto;
        height: auto;
    }
    DataTable {
        width: 150;
        height: 1fr;
        margin: 0 0 0 1;
    }
    .sttic {
        width: auto;
        height: auto;
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
        yield Static(f"┌────── GSI6 Menu ──────┐ ┌───────────────────────────── {self.app.choosed_gsi_name[:-4]} ──────────────────────────────┐", classes="sttic")
        with Horizontal():
            yield OptionList("Kaspersky Info", "System", "Programs", "Process", "Services", "Ports", "Network",
                            "Events", "KLnagchk")
            with Grid(id="details"):
                yield Static(id="text", classes="sttic")
                yield DataTable(id="table", zebra_stripes=True)
                yield Input(placeholder="➤ Search...", id="search")


        # yield Static("└───────────────────────┘ └─────────────────────────────────────────────────────────────────┘")
        yield Footer()

    def fill_table(self, result):
        table = self.query_one("#table", DataTable)
        table.clear()
        table.display = True
        search = self.query_one("#search", Input)
        search.display = True
        search.focus()
        for process in result:
            table.add_row(process["Protocol"],
                          process["Process"],
                          process["Source_ip"],
                          process["Source_port"],
                          process["Destination_ip"],
                          process["Destination_port"],
                          process["Status"],
                          )

    def on_mount(self):
        table = self.query_one("#table", DataTable)
        table.display = False
        search = self.query_one("#search", Input)
        search.display = False
        static = self.query_one("#text", Static)
        static.display = True
        table.cursor_type = "row"
        table.add_columns(
            "[bold][green]Prtcl[/][/]",
            "[bold][green]Process[/][/]",
            "[bold][green]Src IP[/][/]",
            "[bold][green]Src Port[/][/]",
            "[bold][green]Dest IP[/][/]",
            "[bold][green]Dest Port[/][/]",
            "[bold][green]Status[/][/]",
        )

    def on_input_changed(self, event: Input.Changed):
        text = event.value.lower()

        filtered = []

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
        self.fill_table(filtered)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        selected = event.option.prompt
        table = self.query_one("#table", DataTable)
        table.display = False
        search = self.query_one("#search", Input)
        search.display = False
        static = self.query_one("#text", Static)
        static.display = True

        if selected == "Kaspersky Info":
            if self.app.updater1:
                klproducts = ""

                for i in self.app.result["InstalledProduct"]:

                    if "Kaspersky" in i or "Сервер администрирования" in i or "Агент администрирования" in i or "Плагин управления" in i:
                        klproducts = klproducts + "▪ " + i + " (" + self.app.result["InstalledProduct"][i]["Version"] + ")" +"\n" + "                 "
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

#                 avstate = f"""▏[bold][lightgreen]ANTI-VIRUS STATISTIC (AVSTATE)[/]
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
#                 self.app.text0 = f"""▏[bold]GENERAL INFORMATION[/]
# ▏[dim]OS:............[/] {self.app.result["OperatingSystem"]["Caption"]} {self.app.result["OperatingSystem"]["Version"]}
# ▏[dim]Processor:.....[/] {self.app.result["Processor"]["Name"]}
# ▏[dim]GSI ver:.......[/] {self.app.result["gsi_ver"]}
# ▏[dim]Memory:........[/] {str(int(self.app.result["OperatingSystem"]["TotalVisibleMemorySize"]) // 1000)} Mb
# ▏[dim]KL Products:...[/] {klproducts}
# ├――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――\n"""+avstate+"――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――"

                self.app.updater1 = False

            self.query_one("#text", Static).update(self.app.text0)

        elif selected == "System":

            if self.app.updater2:
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
"""+disks
                self.app.updater2 = False

            self.query_one("#text", Static).update(self.app.text1)

        elif selected == "Programs":

            if self.app.updater3:
                self.app.text2 = f""" [bold][lightgreen]Name                                                                         Version[/][/]"""
                procs = []

                for _ in self.app.result["InstalledProduct"]:
                    procs.append(_)
                procs.sort()
                for i in procs:
                    self.app.text2 = self.app.text2 + f"\n [lightgray]{i}[/][dim]{str("." * (77 - len(i)))}{self.app.result["InstalledProduct"][i]["Version"][:15] if "+" not in self.app.result["InstalledProduct"][i]["Version"] else self.app.result["InstalledProduct"][i]["Version"][:15].split("+", 1)[0]}[/]"
                self.app.updater3 = False

            self.query_one("#text", Static).update(self.app.text2)

        elif selected == "Process":

            if self.app.updater4:
                self.app.text3 = f""" [bold][lightgreen]Process                       Version           Full Name[/][/]"""
                apps = []

                for _ in self.app.result["Process"]:
                    apps.append(_)
                apps.sort()
                for i in apps:
                    self.app.text3 = self.app.text3 + f"\n [lightgray]{i[:30]}[/][dim]{str("." * (30 - len(i)))}{self.app.result["Process"][i]["Version"][:15] if "+" not in self.app.result["Process"][i]["Version"] else self.app.result["Process"][i]["Version"][:15].split("+", 1)[0]}{str("." * (18 - len(self.app.result["Process"][i]["Version"][:15])))}[/]{self.app.result["Process"][i]["Product_name"][:50]}[dim]{str("." * (50 - len(self.app.result["Process"][i]["Product_name"][:50])))}[/]"
                self.app.updater4 = False

            self.query_one("#text", Static).update(self.app.text3)

        elif selected == "Services":
            if self.app.updater5:
                self.app.text4 = f""" [bold][lightgreen]Process                       Version           Full Name                            State[/][/]"""
                apps = []

                for _ in self.app.result["Services"]:
                    apps.append(_)
                apps.sort()
                for i in apps:
                    self.app.text4 = self.app.text4 + f"\n [lightgray]{i[:30]}[/][dim]{str("." * (30 - len(i)))}{self.app.result["Services"][i]["Version"][:15] if "+" not in self.app.result["Services"][i]["Version"] else self.app.result["Services"][i]["Version"][:15].split("+", 1)[0]}{str("." * (18 - len(self.app.result["Services"][i]["Version"][:15])))}[/]{self.app.result["Services"][i]["Product_name"][:36]}[dim]{str("." * (36 - len(self.app.result["Services"][i]["Product_name"][:36])))} {"[green]Running[/]" if self.app.result["Services"][i]["State"] == "Running" else "[red]Stopped[/]"}[/]"
                self.app.updater5 = False

            self.query_one("#text", Static).update(self.app.text4)

        elif selected == "Ports":
            self.query_one("#text", Static).display = False
            self.query_one("#search", Input).display = True
            self.query_one("#table", DataTable).display = True
            if self.app.flag:
                self.fill_table(self.app.result["OpenPorts"])
                self.app.flag = False
            pass

        elif selected == "Network":
            self.query_one("#text", Static).update(self.app.result["net_diag"])
            pass

        elif selected == "Events":
            self.query_one("#text", Static).update(" Your advertisement could be here 🥺🥰")
            pass

        elif selected == "KLnagchk":
            self.query_one("#text", Static).update(self.app.result["Network_Agent_report"])

    def action_back(self):
        self.app.updater1 = True
        self.app.updater2 = True
        self.app.updater3 = True
        self.app.updater4 = True
        self.app.updater5 = True
        self.app.updater6 = True
        self.app.updater7 = True
        self.app.updater8 = True
        self.app.updater9 = True
        self.app.flag = True
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
        self.updater1 = True
        self.updater2 = True
        self.updater3 = True
        self.updater4 = True
        self.updater5 = True
        self.updater6 = True
        self.updater7 = True
        self.updater8 = True
        self.updater9 = True
        self.text0 = ""
        self.text1 = ""
        self.text2 = ""
        self.text3 = ""
        self.text4 = ""
        self.text5 = ""
        self.text6 = ""
        self.text7 = ""
        self.text8 = ""
        self.flag = True


    def on_mount(self):
        self.push_screen(ChooseGSI())










if __name__ == "__main__":
    GetSystemInfoUtilityParser().run()