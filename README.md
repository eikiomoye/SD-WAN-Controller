# SD-WAN-Controller
SD-WAN (Software Defined Wide Area Networking) is widely regarded as the future of  networking as it integrates programmable features into its architecture. A new architecture is proposed with the aim of improving end-to-end protocol performance.
SD-WAN Implementation Repository
This repository contains resources, scripts, and documentation related to the implementation of a Software-Defined Wide Area Network (SD-WAN) solution.

Overview
SD-WAN is a revolutionary approach to networking that utilizes software-defined networking (SDN) principles to optimize and manage wide-area networks. This repository serves as a comprehensive guide and resource hub for implementing and understanding SD-WAN technology.

Table of Contents
Getting Started
Key Features
Requirements
Installation
Usage
Contributing
License
Getting Started
To develop an SD-WAN controller in GNS3, first understand SD-WAN architecture and protocols. Set up GNS3 and configure devices to represent the SD-WAN network. Choose and install an SD-WAN controller (in this case an Ubuntu Docker container is used). Design the network topology, connect devices to the controller, and configure it to manage traffic. Test different scenarios, troubleshoot issues, and document the process for experimentation and refinement.

Key Features
Detailed implementation guides
Sample configurations and scripts
Troubleshooting tips and best practices
Case studies and real-world use cases
Requirements
List of prerequisites and system requirements needed to utilize the SD-WAN resources provided in this repository.

Python 3.7+
Ubuntu Docker Container
Access to network devices for configuration in GNS3
Installation
To install GNS3:

Download GNS3: Visit the GNS3 website and download the appropriate installer for your operating system (Windows, macOS, or Linux).

Install GNS3: Run the downloaded installer and follow the on-screen instructions. Once installed, launch GNS3.

To install Ubuntu Docker container in GNS3:

Download Ubuntu Docker Container: In GNS3, go to "Preferences" > "Docker" and download the Ubuntu Docker container image.

Create Ubuntu Docker VM: Create a new project, drag and drop the "Ubuntu" Docker container to the workspace, and start the container.

To install Python modules in the Docker container:

Access Docker Container: Once the Ubuntu Docker container is running, access it by right-clicking and selecting "Console" or using SSH.

Install Python: Update the package lists for upgrades and install Python.

sudo apt-get update
sudo apt-get install python3
Install Python Modules: Use pip to install Python modules as required.

sudo apt-get install python3-pip
pip3 install <module_name>
Repeat the last step for any additional Python modules needed within the Docker container. Adjust the package names as required.

Usage
Demonstrate how to use the resources and scripts included in the repository to implement SD-WAN in your environment.

Contributing
Instructions for contributors, including guidelines, code of conduct, and steps to submit pull requests is based on the procedures of GitHub.
