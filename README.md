# chaos-installer
Complete automation tool for installing/uninstalling Chaos products. Support all Chaos products on Windows, Linux, and MacOS systems.

# Disclamer
FTP and HTTP connection information has been removed due to their sensitivity. This will make the code unusable but it will still demonstrate my programming skills.

# Overview
QA and Support Teams' daily tasks require multiple installations/uninstallations of various versions of the products. This althought simple task requires some efforts from the team-members and also causes some inconviniences. The main idea of the tool as to optimize/automate this process and to make it much more plesant for the engeneer.

# Challenges
### First challenge:
Huge variations of Chaos Products and their versions. There aren't common standards established between different products and versions. Naming conventions, environment variables, parameters and etc are very different from product to product and from version to version. This extreme versatility requires from lots of classes and functions to be aware of those dicrepancies in order to properly install and remove the software.
### Second challenge:
Different Host Platforms (DCC) integrations. Chaos products support more than 10 different host applications. For each host application Chaos products support at least the latest 5 versions. Similarly as the first challenge there aren't established standards between different host-applications, different versions of the host applications and in combination with the first-challenge the complexity of the classes and fucntions increased even more.
