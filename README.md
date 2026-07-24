# Kaspersky GetSystemInfo Parser
The script is a CLI utility in a TUI format. 
Eliminates the need to manually review a GSI5 or GSI6 report by presenting data in human-friendly form.
### Demo
![UI-demo.gif](URL)
### What information does the GSI report provide us with?:

- Kaspersky info:
  <details>
    
        GENERAL INFORMATION
          Opertaing system;
          Processor;
          GSI version;
          Memory (RAM);
          Installed KasperskyLab Products;
  
        ANTIVIRUS STATISTIC (AVSTATE)
          KSC (Administration server) address;
          Host ID;
          AntiVirus Installed (YES/NO);
          AntiVirus Running (YES/NO);
          AntiVirus Bases Date;
          Last Scan Date;
          Last Connect;
          Dynamic VM;
          Ex Tenant ID;
  </details>

- System:
  <details>
  
        COMPUTER
          Processor;
          Processor Cores count;
          Manufacter
          Computer model;
          System date;
      
        BIOS
          Name;
          Version;
          Date;
      
        MISCELLANEOUS
          Procs count;
          Users count;
          Architecture;
          Domain part;
          Domain;
          Workgroup;
          Computer name;
          User name;
          System type;
      
        MEMORY
          Physic;
          Available (physic);
          Virtual;
          Available (virtual);
      
        LOCAL DISKS STRUCTURE
          Disk name;
          Type;
          File system;
          Total space;
          Free space;
  </details>
  
- Process -  List of running processes at the time the GSI report was collected
  
- Services - List of services on the device at the time of GSI collection (started, stopped, manually)
  
- Ports - List of processes, what protocol is used, source and destination IP address, and ports used and status
  
- Network - Output of various network commands, for example:
  <details>
    
        1. Checking connection with the KL activation servers;
        2. A similar check, but for KL update servers;
        3. Command output:
        - ipconfig /all
        - netsh interface ipv4 show route
        - netsh interface ipv6 show route
        - netsh interface ipv4 show subinterface
        - netsh interface ipv6 show subinterface
  </details> 
- Events - .evt(x) logs with events generated over 3 days, such logs as:
  <details>
    
        - Application;
        - System;
        - Kaspersky Events Logs;
        - Kaspersky Endpoint Security;
  </details>
- KLnagchk - Output of the results of the utility of the same name, i.e. Network Agent connection statistics

- HOSTS - HOSTS file of the same name from the device

### Guide how to get Kaspersky GSI5 or GSI6 report:
[ENG](https://support.kaspersky.com/common/utility/3632) [RU](https://support.kaspersky.ru/common/utility/3632)
