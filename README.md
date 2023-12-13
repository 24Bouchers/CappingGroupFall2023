# RadiusUI.py
Archtop Fiber/GTel Marist Capping Project Fall 2023

Steven Boucher <br>
Easton Eberwein <br>
Nick Vasquez <br>
Liam Haggerty <br>
Christian Bauer

## Table of Contents

- [Introduction](#introduction)
- [Endpoints](#endpoints)
- [Tables](#tables)
- [Dashboard](#dashboard-page)
- [Devices](#devices-page)
- [Logs](#logs-page)
- [User](#users)
- [Bugs](#Bugs)
- [Frontend Framework](#frontend-framework)
- [Using Bootstrap](#using-bootstrap)

## Introduction

This document will explain how to navigate the site that our group has created. There are three pages for the user to navigate on our site, each with different functionality. Dashboard (index.html), Devices (devices.html), and Logs (logs.html) 

RadiusUI is an API designed to allow GTel employees to insert static IP addresses through their website and verify through
their FreeRADIUS servers. This webpage also displays relevant data about their servers, connectivity, MAC addresses, and IP Addresses.

## Endpoints

The API currently connects to a web server and two MariaDB servers hosted by Gtel.<br>
The API was tested on a web server (http://10.10.9.40:5000) and a MariaDB server (10.10.9.43) hosted by Marist College.

## Tables 

Four tables keep the API functional. Three are GTel-created tables with the logs table created by the Marist students listed above. Pictured in the Table_Flow.png is an ERD/Flowchart describing how the tables are used/appear. <br>

 [Linked is the Lucid Chart Diagram](https://lucid.app/lucidchart/98f36848-a34a-496a-aea1-8b74693481a4/edit?viewport_loc=-435%2C13%2C2602%2C1311%2CzxEJecSUvRbf&invitationId=inv_0f03a49c-5bfb-4f13-b19e-6fabd795f66e)

## Dashboard Page

The dashboard is the home page for our API, which has various pieces of information displayed. The total number of devices, how many devices are currently online, how many static IP accounts exist, and how many IP addresses are unreachable. 

A dynamic graph displays the total number of requests for IP addresses and updates every 15 minutes, showing the last 6 hours of data. This graph will show crucial information about GTel servers, such as spikes in requests due to power outages. If the graph lines are too sharp or too curvy, there is a lineTension vaiable on line 200 in index.html that can be ajusted. 0 represents no curve and 1 represents deep curves.

On the right-hand side is a System Status, a quick check to ensure that FreeRadius and the SQL server are working appropriately.

## Devices Page

All Devices in the system are displayed here.
On this page, there are multiple functions that the user can use.

The first function is the Add Device function, which allows the user to add a new device to the system. The user enters the MAC Address or the username for the radcheck and radreply tables, the IPv4 Address, The IPv6 Prefix, and the IPv6 Address. If added correctly, a message will indicate that the device was added successfully! The logs table is updated to reflect that the new device has entered the system.

The second function is the Edit Device function. Each device has an edit button on the far right of the table. When pressed, it will take the user to the Edit Device page, where the user can input an IPv4, IPv6 Prefix, and an IPv6 address. After pressing the confirmation button, the API will update the database to reflect the changes and create a new entry on the logs table.

The third and final function is the Remove Device function. This function allows a user to remove a device from the database. By clicking on the “Remove” button next to the device you wish to remove, a message will pop up, prompting the user with the message: “Are you sure you want to remove this device?” to which the user must click “OK.” ensuring that the user cannot delete a device accidentally. Removing a device also updates the logs table.

There is a search bar that allows the user to search for a given device based on username/MAC, IPv4, or IPv6 addresses.

## Logs

The logs page displays whenever a change transpired to the Devices page. The Logs table displays when an update happened, the MAC addresses/Users, and what happened. 

## Users

This part of the site is still in progress and is a stretch goal. We have left a users.html and login.html for future groups and commented out the navigation code in the other HTML files.

When implemented, this will show basic information about the currently signed-in use. The Logs page will have an additional column to show who makes what update.

## Bugs

The only currently known bug is if the user searches for a device or log that does not exist, the user will have to refresh the page to clear the search.

Note: for the graphs, be careful what time zone the server/vm is compared to the localhost when testing.
App.py's date.today() pulls from the machine it is running on and thus can appear a day behind if in EST, as the data is in UTC.

## Front-end Framework

The site uses the Bootstrap framework for its front-end design. Bootstrap is a popular open-source toolkit for developing with HTML, CSS, and JS. It provides ready-made components and responsive design features that make web development more accessible and efficient.

## Using Bootstrap

Bootstrap’s grid system, components, and utilities are used extensively throughout the site to create a responsive and visually appealing interface. This choice of framework enables rapid prototyping and a consistent look and feel across different pages.

Here are some key aspects of our site’s design that leverage Bootstrap:

1. Responsive Layout: Utilizing Bootstrap's grid system, the site is fully responsive and adjusts seamlessly across different screen sizes and devices.

2. Components: Various Bootstrap components like navigation bars, forms, buttons, and cards are used to maintain uniformity in design.

3. Customization: While we rely on Bootstrap for the majority of the styling, custom CSS has been written to further tailor the look and feel to match our specific design requirements.

4. Consistency: Bootstrap's comprehensive component library ensures a consistent and modern user interface, enhancing usability and aesthetics.

## Contact

Steven.Boucher1@marist.edu <br>
Easton.Eberwein1@marist.edu <br>
Liam.Haggerty1@marist.edu <br>
Nicklas.Vasquez1@marist.edu <br>
Christian.Bauer1@marist.edu <br>

[Project Link](https://github.com/24Bouchers/CappingGroupFall2023)