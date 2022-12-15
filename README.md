# chaos-installer
Complete automation software for installing/uninstalling Chaos products with support for:
* All Chaos products
* All Operating Systems Windows, Linux, and macOS.
* All installation types (Official, Nightly, ZIP/Arbitrary)
* Product Uninstallation
* License Listener
* Settings

# Overview
QA and Support engineers' daily tasks require multiple installations/uninstallations of various versions of the products. This although a simple task requires some effort from the team members and also causes inconveniences. The main idea of the tool is to optimize/automate the process of downloading and installing the software and make it much more pleasant for the engineer.

# Challenges #

### First challenge:
Huge variations of Chaos Products and their versions. There aren't common standards established between different products and versions. Naming conventions, environment variables, parameters, etc are very different from product to product and from version to version. This extreme versatility requires lots of classes and functions to be aware of those discrepancies to properly install and remove the software.

### Second challenge:
Different Host Platforms (DCC) integrations. Chaos products support more than 10 different host applications. For each host application, Chaos products support at least the latest 5 versions. Similarly, as the first challenge, there aren't established standards between different host applications, and different versions of the host applications and in combination with the first challenge, the complexity of the classes and functions increased even more.

### Third Challenge:
Different Operating Systems. The tool supports Windows, Linux, and macOS. Most of the functions have completely different implementations between the different Operating Systems. 

Combining the above points with a variety of internal functions makes the whole project a lot more complex than it looks on the surface.

# Disclamer
FTP and HTTP connection information has been removed due to their sensitivity. This will make the code unusable but it will still demonstrate how the tool is built.

# Technology
The project is built mainly on Python and PyQt. Of course, many python standard libraries have been used to deliver additional functionality like:
* os, json, time, datetime, sys, platform, tempfile, subprocess, operator, logging, shutil, ftplib, re, requests, winreg, zipfile, pathlib, threading, csv, signal, xml.etree.ElementTree, asyncio.format_helpers

# What I learned
* How to build software that supports multiple OSes
* How to build GUI applications with PyQT library
* How to build software entirely on OOP
* Work with Windows Registry
* How to run processes on separate threads

# Examples
![image](https://user-images.githubusercontent.com/74985932/207979018-c6c9885c-9421-4ab7-9125-671788fd66de.png)
![image](https://user-images.githubusercontent.com/74985932/207979194-66666470-8b62-40e0-a352-1b16f1b58417.png)
![image](https://user-images.githubusercontent.com/74985932/207979237-61648f34-a6af-4a57-ad69-a5417c74a535.png)
![image](https://user-images.githubusercontent.com/74985932/207979276-626df7f2-9bac-4e87-b101-2a3a775392d6.png)
