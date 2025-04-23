# *JobViewer*: Graph-based Visualization for Monitoring High-Performance Computing System

Tommy Dang *Department of Computer Science Texas Tech University* Lubbock, Texas, USA tommy.dang@ttu.edu

Alan Sill *High Performance Computing Center Texas Tech University* Lubbock, Texas, USA alan.sill@ttu.edu

Ngan V.T. Nguyen *Department of Computer Science Texas Tech University* Lubbock, Texas, USA ngan.v.t.nguyen@ttu.edu

Jon Hass *Dell Inc.* Austin, Texas, USA jon.hass@dell.com

Jie Li *Department of Computer Science Texas Tech University* Lubbock, Texas, USA jie.li@ttu.edu

Yong Chen *Department of Computer Science Texas Tech University* Lubbock, Texas, USA yong.chen@ttu.edu

*Abstract*—Visualization aims to strengthen data exploration and analysis, especially for complex and high-dimensional data. High-performance computing (HPC) systems are typically large and complicated instruments that generate massive performance and operation time series. Monitoring HPC systems' performance is a daunting task for HPC admins and researchers due to their dynamic natures. This work proposes a visual design using the bipartite graph's idea to visualize HPC clusters' structure, metrics, and job scheduling data. We built a web-based prototype, called *JobViewer*, that integrates advanced methods in visualization and human-computer interaction (HCI) to demonstrate the benefits of visualization in real-time monitoring HPC centers. We also showed real use cases and a user study to validate the efficiency and highlight the current approach's drawbacks.

*Index Terms*—High-Performance Computing Center, Job Scheduling, Radar Charts, Time-Series Data Analysis, Multidimensional Data Visualization

# I. INTRODUCTION

With the advancement of High-Performance Computing (HPC) systems towards scale and complexity, the monitoring task is becoming increasingly important and challenging. Comprehensive understandings of the system status, resource utilization, and user usage behavior are critical in the operating procedures. However, the veracity and volume of data generated every day by an HPC system make monitoring a daunting task. This complexity simultaneously introduces a silver lining in enormous research opportunities for researchers and system administrators to investigate the dynamic nature and the interconnection between numerous components within the system.

Visualization facilitates these complex monitoring tasks by providing an intuitive and analytical means for data tracking, exploration, and analysis. In most cases, the HPC data often comes in the form of temporal, multidimensional measurement data, where data points arrive in data streams at different time intervals. Prior literature has investigated the temporal characteristics to extract meaningful insight, where each record (or entry) is a function of time, including real-time I/O monitoring [1] by Betke and Kunkel, or whole-system monitoring [2] by Agelastos et al. Recently, Schwaller et al. [3] has proposed a system data pipeline where visualization is incorporated as a core component in an analysis-driven approach supporting multi-cluster HPC centers. However, the existing work views essentially from a time-series perspective where each record is a function of time, specifically demonstrated in multiple dashboards with time as a linear, horizontal axis. How these jobs utilize system resources, and *to what extent* user activities influence upon system's state by taking into account the relation between jobs submission data and computing resources are unexplored.

Having the answers to these questions would play an essential indicator for both system administrators and system users. It allows them to put their perspectives upon HPC system analysis beyond the temporal dashboards and the usage pattern and interconnections between system components. For system administrators, looking at the related attributes or associated factors assists a thorough examination of system failure: track provenance, perform investigative analysis, provide a timely mechanism in critical conditions and mitigate future incidents. For users, they often carry out an estimation of the runtime of a job for system scheduling, which is generally inaccurate [4], causing forced termination before completion or prolonged queuing time. This information of the computing node health and job itself would support them in making informed decisions.

To represent a structure that comprises multiple entities and their connections, we constructed a graph-based visualization, also known as network visualization. Shneiderman and Aris [5] indicated the goal of network visualization lies in the ability to ensure visibility of the network with an increasing number of nodes and links while maintaining the comprehensibility in assisting task completion. The sizes of nodes and links for the HPC data are substantial, but the

978-1-6654-6090-3/22/$31.00 ©2022 IEEE DOI 10.1109/BDCAT56447.2022.00021

multidimensional characteristics also aid the complex analysis. The approach of multiple levels of detail is demonstrated by Liu et al. [6], where each machine cluster is surrounded by its applications, having color as the indicator of abnormality. We find this design effective in diagnosis tasks; however, applying scalability with approximately 500 computing nodes is challenging. The authors in [5] argued that the spatial approach with nested or hierarchical clusters supports users to "navigate large graphs, focus on regions of interest". For a complex network topology, a bipartite graph proves its advantages in visualizing multiple entities originated from two disparate sets [7]. In the case of HPC data, we wanted to visualize the placement of such node groups to simulate the location of different computing racks.

This work presents a novel method for monitoring temporal, multidimensional HPC system data with interactive graph visualization and animation technique. The core component of the visualization is a bipartite graph, having nodes in the network aggregated in a nested manner while preserving the general topology. To the best of our knowledge, no existing work has explored the analysis of jobs submitted by users according to the computing node health from a graph-driven perspective, making this a unique contribution. By coupling interactive visualization with HPC data analytics, we show that users can explore the interconnection between system components and discover the outliers/hot spots with associated attributes within the system. The main contribution of this work can be laid out as:

- An interactive visualization for monitoring job accounting data, called *JobViewer*, which: 1) takes into account the relations between users and computing nodes, 2) shows an automatic progressive snapshot of system status, and 3) allows quick detection on unusual events.
- The visual demonstrations of the proposed approach by applying it to real data acquired from an HPC center.
- The validation of the usefulness of the visualization by conducting an informal user study.

The rest of this paper is organized as follows: Section II summarizes existing works that are close to our paper. Section III presents the design rationale and tasks analysis. Section IV shows the findings through use cases with the real HPC data. Section V demonstrates the informal user study that we conducted for this work. Section VI presents the discussion we have around *JobViewer*. Section VII concludes our paper with outlook for future work direction.

# II. RELATED WORK

# *A. HPC Performance Monitoring*

The task of monitoring HPC performance is becoming increasingly relevant, thus the growing volume of research work in recent years. Misra et al. proposed CHReME [8], a web-based interface for monitoring HPC resources that allows a "layer of abstraction" which helps alleviate the complication that end-users face with the conventional command lines. Splunk [9] by Carasso is another software platform for mining and investigating log data for system analysts. Its most significant advantages are the capability to work with multiple data types such as comma-separated values (CSV) or JavaScript Object Notation (JSON) in real-time. It has been used and shown consistent performance in the subsequent studies of Stearley et al. [10], followed by Zadrozny and Kodali [11]. However, recently, Greenberg and Debardeleben [12] pointed out that Splunk was not feasible for searching within a vast amount of data generated every day (e.g., hundreds of gigabytes of data) due to slow performance.

Regarding technical tools, Ganglia is an open-source distributed monitoring system for clusters and grids. The strength of Ganglia is the scalability on clusters of up to 2000 nodes and federations of up to 42 sites [13]. This tool uses RRDtool [14] to store and visualize time series data. Nagios [15] is another tool that many organizations utilize for monitoring a variety of servers and operating systems with industrial standards. The tool has two versions: one commercial (Nagios XI) and open-source (Nagios Core) [16]. Nagios provides the flexibility in listening to event handlers and executing a plugin upon a request for service or host status check. Amazon cloudwatch [17] allows end-users such as system administrators and system architects to monitor their Amazon Web Services (AWS) applications in the cloud in near-realtime.

Job scheduling and resource management are the fundamental problems of efficiently utilizing HPC systems [18], [19]. The researchers at Texas Tech University have already implemented to develop a set of easy-to-use and holistic interactive interfaces to meet domain scientists and system administrators' needs [20], [21]. Figure 1 shows an example of the TimeRadar [22] visual interface we intend to have for visualizing multivariate resource metrics together with job data [23]. The multivariate resource metrics of compute nodes over an observed period are first clustered into ten major color-encoded groups, as shown at the bottom of Figure 1. On the timeline view in the left panel, every line represents a compute node (or a group of compute nodes with similar visual signatures). Compared to these visualizations, our proposed *JobViewer* mimics the spatial layout of the HPC centers. The application assists the administrators in identifying irregular events; not only when the events happen but also where they are located and if there are any spatial relations of the related computing nodes in the HPC systems.

Grafana [24] supports integrated visualization widgets (e.g., line charts, bar charts, and heatmaps). In particular, Grafana defines a place holder (i.e., panels) for basic charts of the selected metrics, which is easy to modify even for non-expert users. This visualization package has been used in various work [1], [12] due to its multiple data storage features and flexibility. However, this is also a limitation of Grafana: it does not natively support customized or advanced visualization techniques for analyzing high-dimensional data (such as parallel coordinates [25] and scatterplot matrices [26], [27]). Besides a standalone web version, this work also introduces a Grafana plugin of *JobViewer*. This helps increase the accessi-

![](_page_2_Figure_0.png)

Fig. 1. TimeRadar visualizationfor real-time monitoring HPC systems [22] : (left) resource metrics timeline which are projected into 10 major groups at the bottom; (right) job information and user statistics such as total energy usage (kWh) per job/user (calculated with resource metrics and job data).

bility of the proposed work so that it can be easily adapted to monitor different HPC systems.

# *B. Graph-based visualization*

A number of graph-based visualization techniques have been proposed in previous work. Shneiderman and Aris [5] present the idea of *semantic substrates*, which is the "nonoverlapping regions in which node placement is based on node attributes". This aligns with our design of the bipartite network (will be discussed further in Section 3), where the computing nodes are divided by the rack they belong to. Liu et al. [6] demonstrates contextual exploration across analysis levels in exploring semantic graph layout in both top-down and bottom-up directions, independent of human bias. McLachlan et al. presents LiveRAC [28], a time-series data visualization emphasizing on high information density. Besides the temporal overview, the user can carry out semantic zooming for further detail. The issue of visualizing two disjoint sets of elements is carefully elaborated in Ocelot by Arendt et al. [29]. Given the numerous potential layouts of network visualization with the huge number of nodes, visual space and clutter are the two main considerations for visibility and comprehensibility [5].

#### III. DESIGN RATIONALES AND DECISIONS

Based on our weekly discussions with the domain experts, the HPC visualization requirements are expanded on the following dimensions: HPC spatial layout, temporal domain, resource allocations, and system health metrics such as CPU temperature, memory usage, and power consumption. We, therefore, focus the following design goals on (D1) Provides spatial and temporal overview across hosts, racks, and scheduled jobs, (D2) Provides the holistic overview of the system on health metrics and job scheduling data at a selected timestamp. (D3) Highlights the correlation of system health services and resource allocation information within a single view, and (D4) Allows system administrators to drill down a particular user/job/compute to investigate the raw time series data for system debugging purposes. While it is straightforward to visualize system structure, different health metrics, and job scheduling data on multiple coordinated views [28] and use brushing and linking to perform filtering, integrating these data into a single display provides a more comprehensive overview and supports the visual reasoning processes [30].

Figure 2 depicts four main components of the *JobViewer*, including the timeline, main visualization, control panel, and the job table. Let us first consider the timeline in Figure 2(a). We use animation to illustrate the temporal flow of the dataset. Animation has positive impacts on cognitive aspects such as interpreting, comparing, or focusing [31]. Although this method cannot grasp the full temporal information (only a single snapshot of the system can be shown at a selected

![](_page_3_Figure_0.png)

Fig. 2. The main components of *JobViewer*: (a) Timeline selection, (b) main bipartite visualization, (c) control panel, (d) job table and time series.

timestamp), it is convenient for both: analyzing historical data and visualizing the system in real time. The timeline also supports quickly investigating time steps of interest by a single click/drag on the time slider.

Figure 2(b) shows the main visualization at a particular time step. The design bases on the idea of the bipartite graph with two disjoint sets of vertices. One set contains users, and another consists of the computing nodes. The link between a user with a computing node implies that the node is running at least one job of the user (Design goal D3). We design this graph with all users in the central list and all computing nodes surrounding it. The computing nodes are divided into ten racks as their actual spatial locations. A benefit of graph-based visualization is that it is easy to highlight the link between a user and a computing node. For instance, we implement the mouse over the user or the computing node to highlight the corresponding vertex's links. The graph-based design also allows us to apply a simple visual method for illustrating the computing nodes' health metrics. *JobViewer* uses color to display the value of a chosen metric. The map from color to value is depicted by the color scale on the control panel tab, as can be seen in Figure 2(c). In brief, we use various visual communication channels to display all four required dimensions (time, physical information, job scheduling data, and health metrics readings) of the HPC multidimensional dataset in a comprehensive layout.

Besides the above designs, we also implement other visual effects to give related information and improve the cognitions. It is easy to recognize a new user appearing on the central list via animation; however, if a current user (who has some jobs running somewhere in the system) runs a new job, it is difficult to identify. If this case happens, we highlight the user at the corresponding time step by its outline and the color of links to computing nodes allocated the new jobs. About the computing nodes, one may wonder how many jobs a computing node is running. We indicate the number of jobs running on a computing node by thicker outlines. Additionally, if the chosen metric's value on a computing node varies significantly over two consecutive time steps, we use the blur effect to highlight the sudden change. While we do not have enough space to include these visual encodings in this paper, we refer the reader to the accompanying video with these examples.

Figure 2(c) shows the control panel and all options of the dropdown menus. There are two options for displaying on the central list: the current HPC users and the running jobs. Users can rank the central user list via three options: total number of jobs, the number of allocated nodes, and the health metrics. We can also select one of the nine metrics to color the node's backgrounds. Two more options beyond health metrics are user/job name and radar charts [32]. An example of radar charts is given at the bottom of Figure 1. If we select the user/job option, all computing nodes are colored according to the users/jobs that they belong to. If we select the radar view, *JobViewer* visualizes every computing node by a radar chart summarizing all its health metrics.

However, suppose we visualize the computing nodes by their radar chart. In that case, it is difficult to recognize the shapes because their sizes appear relatively small to be visually discerned in the overall layout. Through the informal discussions with the domain experts, we found that color is more effective for cognitive activities. It is the reason why we apply clustering algorithms to group the computing nodes based on their health metrics. Then, we color each cluster a different color. Every radar chart representing a computing node has the color of its group. This method also improves the analyzing process because it reduces 467 computing nodes to a much smaller number of patterns of health states. We can quickly gain characteristics of the system states or detect strange behaviors of some computing nodes. Two clustering algorithms integrated into *JobViewer* are k-means and leader algorithm [33].

Another interaction with the main visualization is the mouse click to show the corresponding table of jobs' information, as seen in figure 2.d. On the table, we can find all information related to the jobs, such as the job's identity, job name, HPC users, number of cores the job is using, etc. (Design goal D4). Moreover, we also display the time series of the selected health metric on the clicked computing node, and we highlight the period when the job runs on that computing node by the grey area. This visualization helps us understand what happens with computing nodes when particular users are using them. As we will show in the next section, this feature may give information about relations between jobs or users with computing nodes' health states.

To sum up, the proposed solution visualizes the HPC system as a bipartite graph, where jobs are connected with nodes via graph edges, clearly indicating the correspondence, and nodes are colored based on the desired factor, e.g., CPU temperature. It also integrates some simple visual methods and clustering algorithms to support cognitions for the analyzing process. The *JobViewer* layout and its visual encodings have undergone multiple iterations with the HPC experts and users through our weekly discussions. The following sections demonstrate how we can use *JobViewer* in monitoring an HPC system.

# IV. USE CASES

## *A. Monitoring HPC Resource Allocations*

The first use case focuses on job scheduling data. Figure 3(a) shows a snapshot of the main visualization on 08/14/2020 at 5:50 PM. The color distinguishes between different users, along with their related computing nodes. If a computing node runs several jobs of different users, it is filled by all corresponding colors in the circle, as shown in the enlarged circle in Figure 3(b). White circles represent idle

![](_page_4_Figure_7.png)

Fig. 3. Snapshots of the main visualization at (a) 5:50 PM and (b) 6:00 PM on 08/14/2020: Selecting *user0*, the highlight of all its links and related computing nodes appears.

nodes. At 5:50 PM, there are nine white computing nodes that locate in six different racks. Ten minutes later, *user0*'s job starts, as highlighted by the black outline and links in Figure 3(b). It takes 1080 cores, or 30 computing nodes (each computing node has 36 cores): 18 nodes run two jobs, and 12 others run only one job. We have checked and found that most of the 18 computing nodes' former jobs consume all 36 cores at 5:55 PM. It means that some of the computing nodes utilize up to 72 cores, including virtual cores, at 6:00 PM. The system allocates seven out of nine white computing nodes to *user0*, and there are still two available nodes at 6:00 PM (one is on rack 2, and another is on rack 9). This indicates that the system overuses some computing nodes (running multiple jobs) while some are unused. This use case is an example that can illustrate how *JobViewer* supports HPC administrators to monitor job scheduling and resource usage in the system.

# *B. Providing Major Operating Status via Clustering Health Metrics*

This use case investigates the health monitoring aspect of the *JobViewer*. As mentioned in section III, we use color to depict values of a selected health metric from the list of nine. Another option to observe all nine health metrics in a single view is to capture the operating status of computing nodes by radar charts. As the radar size is relatively small to be visually discerned their shapes quickly, we use the color to encode the operating status of the computing nodes. The operating statuses are automatically generated via popular clustering algorithms such as k-means and leader algorithm [33] on the multidimensional health readings of the computing nodes. Specifically in Figure 4, the clusters of node statuses (at the selected timestamp) are computed based on their nine readings: *CPU1 temperature*, *CPU2 temperature*, *Inlet temperature*, *Memory Usage*, *Fan1 Speed*, *Fan2 Speed*, *Fan3 Speed*, *Fan4 Speed*, and *Power Consumption*. The number of clusters is a user input. This option is available when users select visualizing by all metrics in Figure 2(c).

![](_page_5_Figure_3.png)

Fig. 4. (a) Clustering result of the leader algorithm for all 467 computing nodes on 08/18/2020 at 11:30 AM. (b) Visualization of the computing nodes in rack 4 with radar charts representing the computing nodes. The background colors of these radar charts encode their clusters.

Figure 4(a) shows the clustering result of the clustering algorithm for the HPC system at Texas Tech University on 08/18/2020 at 11:30 AM. This algorithm clusters 467 computing nodes into five groups (or five major operating statuses) with different morphologies of their health states. We consider the blue group as normal operating status, 450 out of 467 nodes in the HPC system. We can also see that 13 computing nodes (in the orange, green, and purple groups) do not have fan readings. The red group has four computing nodes with high *fan speeds*, *CPU2 temperature*, and *power consumption*. Figure 4(b) shows that all four red computing nodes belong to Rack 4. We have investigated and found that only the computing node 4.33 has high *CPU2 temperature*. Figure 5(b) confirms this statement, as the color of computing node 4.33 is red while that of the other three is light green. We can also visualize the *CPU1 temperature* of these four computing nodes as depicted in Figure 5(a). Their physical locations are one possible explanation for high fan speeds on computing nodes 4.33, 4.34, 4.35, and 4.36. They locate near each other in Rack 4, so the three computing nodes (4.34, 4.35, and 4.36) may sense the heat from the neighboring node 4.33 and, thus, increase their fan speeds to cool down.

![](_page_5_Figure_7.png)

Fig. 5. The visualization of all computing nodes in rack 4. The color indicates (a) CPU1 temperature and (b) CPU2 temperature. Red color means high value, yellow depicts a medium temperature, and green represents low value.

# *C. Analyzing User Jobs vs. Temporal Health Metrics*

![](_page_5_Figure_10.png)

Fig. 6. Visualizing CPU2 temperature of computing node 4.33. The colored areas highlight the period when a user runs his/her job on 4.33.

This use case analyzes the relations between user jobs and the health states of computing nodes. We firstly look at the time series of *CPU2 temperature* of the computing node 4.33 in Figure 6. The *CPU temperature* is measured in Celcius. The vertical dash line indicates the selected timestamp of the *JobViewer* in Figure 6: 08/18/2020 at 11:30 AM (users can change from the timeline). The colored areas highlight different users/jobs running on the given computing node: We added text notations to denote users and their jobs. As depicted, this one-week example has five jobs on computing node 4.33. None of them overlaps with each other (they do not share node 4.33). The *CPU2 temperature* has a high value when *user1* runs his/her job, but the value suddenly reduces when *user10* starts his/her job. Similar jumps or drops happen when there is a switch of users. Therefore, it is reasonable to state that the CPU2 temperature of computing node 4.33 depends on the job running on it. If we look at the CPU1 temperature of computing node 2.60 in figure 7, we can observe a similar behavior of the dependency. Some jobs are responsible for high CPU temperature, while some jobs do not cause hot CPUs.

![](_page_6_Figure_1.png)

Fig. 7. Visualizing CPU1 temperature of computing node 2.60. The colored areas highlight users/jobs using this node.

Can we use these relations to investigate the reason for the irregular hot CPU2 temperature of computing node 4.33, as mentioned in the previous use case? If we compare the user and job running on the computing nodes, namely 4.33 and 2.60, on 08/18/2020 at 11:30 AM, they run only one job of precisely one user. The value of CPU2 temperature of the computing node 4.33 is also higher than other users, such as *user1* and *user13*. This job is suspicious. *JobViewer* is tasked to help the administrators in monitoring the HPC system and highlighting the unusual events. Further investigations (such as discussing the actual users) are needed to find out the root of the issue.

# V. USER STUDY

# *A. Overview*

We contacted three volunteers, who have experience working with the HPC systems (in both academia and industry), and carried out the user study through video calls. The three users (two males and one female) have three, five, and ten years respectively working in this domain. Two of the three got their PhDs in the HPC-related fields. They all work in the same HPC center at a university, with four computing clusters of different sizes. The most difficult for these HPC administrators is dealing with the large amount of monitoring data generated every few seconds. While the line charts are a standard method for visualizing time series, the HPC administrators have to switch through different views and mentally combine different charts for comparisons. Therefore, an overview of various data sources on the same display is desirable before drilling down further details.

The user study begins with an introduction to the *JobViewer*. The introduction covers all features and functions of four main components. After that, we ask whether the volunteers have questions or any confusion about the application. If they are still unclear about our web-based prototype, we explain carefully again to ensure they fully understand what they can achieve from the *JobViewer*. The next step is to ask them to answer some questions and record their actions while finding the answers. Finally, we ask whether they have feedbacks on the application or not.

We divide the questions into five tasks as the following:

- Health metrics: This task aims to check whether volunteers can gain information about the computing nodes' health states. We require volunteers to select a health metric and name one computing node with a high value of the chosen metric. Also, the volunteers need to point out users linked to that computing node.
- Job information: This task checks whether the volunteers know how to get information about a job. We ask them which user's job starts at a particular time step and some computing nodes allocated for the job.
- Clustering: This task requires the volunteers to understand how to use the clustering algorithms for detecting the computing nodes with irregular health states. The volunteers need to identify and name all computing nodes with a given pattern of health metrics.
- Metric vs. Job relation: This task asks the volunteers to use the time series of a selected metric of a specific computing node to comment on the dependency between the job and the selected metric.
- General comments: This task gets the volunteers' feeling when using *JobViewer* to answer questions in the above tasks. We want to know whether the application is easy for them to find answers to the above questions. Also, we ask whether they think this application is helpful for monitoring activities.

For the task Clustering and Metric vs. Job relation, we aim to ask the volunteers question related to the use case of computing node 4.33, as mentioned in section IV-B. We hope they can see the benefits of our approach through these questions. One user recognizes some issues with computing node 4.33 and spends time investigating it.

## *B. Results*

Overall, two volunteers can quickly go over the questions and use the application quite correctly, while a volunteer fails some of the visualization tasks. The first volunteer moves smoothly to all the questions, except reaching a particular time step. It is difficult for them to observe the time on the timeline because it is too small. Also, they have some issues when trying to reach a specific time step as required by the questions. This volunteer is the only one that spends lots of time on task 4 because he thinks it is interesting to find the reason behind the irregular hot in CPU2 of computing node 4.33, as discussed in

![](_page_7_Figure_1.png)

Fig. 8. It is difficult to read time information and reach a particular time step in the timeline's original design, so we implemented a new component for the timeline. The HPC administrators can click on the right/left button to move toward the time step of interest or type it directly.

section IV-B. He moves the timeline to look at jobs at different periods and switch to various health metrics to understand the situation. He finally ends up with an assumption about the positions of the four computing nodes. The second volunteer also performs well with the tasks, except for the first one. He mentions that red computing nodes correspond to high values of the selected metric, but he decides to pick up a yellow one as the answer. For the task Metric vs. Job relation, he replies that the job consuming high CPU usage will cause high CPU temperature. Regarding their opinions about whether *JobViewer* is helpful for monitoring activities, these two volunteers have common comments. Although *JobViewer* has a good design and is helpful for a human to build up investigations, the monitoring administrators may not spend too much time on any irregular event step by step. They want to catch the problems quickly, so they prefer a large display containing all visual representations side-by-side. Regarding the last volunteer, he comments that the web application is challenging for him to navigate the views he needs. Therefore, he suggested having an input panel to input the computing nodes vs. the users he is searching for.

The first two volunteers also give feedback on how to improve the *JobViewer*. One is the design of the timeline. Because the whole time interval is long, reaching a particular time step may be a challenging activity. Besides, the text on the timeline may be too small for some application's users to read. Taking this feedback into account, we improved our design with a new component above the timeline to make it more usable, as depicted in Figure 8. In particular, users can directly type the time stamp of interest to bring up the *JobViewer* system overview. Another improvement to navigate the timeline is using the right/left button to move back and forth one-time steps. Moreover, the second volunteer mentions the scalability of the *JobViewer* because some HPC clusters may have thousands of computing nodes. Regarding this comment, we believe the graph-based design is suitable for scaling up to a much larger number than the current 467 computing nodes. Two reasons that support this argument are as the following.

- 1) We use color as the primary visual signal to inform the health states of computing nodes. We can select individual HPC users or computing nodes to observe further details and time series. The color helps improve the cognitions if there are too many computing nodes in the system.
- 2) If we have more rack and computing nodes, we can expand the main visualization because it uses a graphbased design. For example, we can use multiple layers of racks. In this case, the links may look cluttered and crowded. However, it can be visually overcome by simple highlights.
# VI. DISCUSSION

The strength of *JobViewer* is its ability to display both system health states and resource allocation information in a single integrated view. Section IV-A discusses how *JobViewer* presents job allocation in the main view. The clustering algorithm integrated into the application can quickly show the major characteristics of the system's health states. From these grouped operating statuses, we can point out any computing node with an irregular health state pattern to investigate the problems behind it. Section IV-B describes a use case for this benefit. Moreover, *JobViewer* can allow us to observe the relations between jobs and computing node health, as illustrating in section IV-C. This feature highlights jobs and users' behaviors to understand them better and to find suspicious causes of any problem. The volunteers in the user study also find it interesting to use this feature to investigate the irregular heat in CPU2 of computing node 4.33.

To use *JobViewer* efficiently, we need the training to know interactions and activities to get desirable information. One volunteer out of three comments on the difficulty of using the visual interface as he is used to working with data in tabular formats, while the other two can quickly go through the tasks. Besides, the timeline's original design is not optimal for long time series, so we improved it, as shown in figure 8 and mentioned in section V-B. Another issue related to *JobViewer* is that it is not a complete tool for HPC monitoring. We focus on the four design goals rather than an efficient and comprehensive tool for commercial purposes. The *JobViewer* is an application that can show the advantages of visualization and human-centered computing in a complex task of HPC monitoring.

As discussed in Section II, we also implemented a Grafana plugin of *JobViewer*. Figure 9 shows the current version of *JobViewer* in Grafana, which can provide real-time monitoring. In particular, two input data sources are required for the deployment of our Grafana plugin: Health metrics data (from the iDRAC [34], the integrated Dell Remote Access Controller for Dell EMC PowerEdge servers), and job scheduling data

| 맘 General / HPC | প্ল 8 |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Nocona | cpu-23-1 ~ UsersNocona | All v | NodeByUser | All ~ | Quanah | cpu-1-1 ~ |
| Control panel |  |  | Job Viewer |  |  |  |
| CPU_usage V |  |  |  |  |  |  |
| 08/11/2021 12:00 AM |  |  | user6 66 jobs |  |  |  |
|  |  |  | user18 11 jobs |  |  |  |
| 4 undefined nodes |  |  | user11 8 jobs |  |  |  |
| ಲಿ |  |  | user1 7 jobs |  |  |  |
| cpu-23-29, cpu-25-50, cpu-25-59, cpu-26- |  |  | user17 5 jobs |  |  |  |
| 27 |  |  | user8 5 jobs |  |  |  |
|  |  |  | user19 2 jobs |  |  |  |
|  |  |  | user16 2 jobs |  |  |  |
|  |  |  | user7 2 jobs |  |  |  |
|  |  |  | user2 2 jobs |  |  |  |
|  |  |  | user13 2 jobs |  |  |  |
|  |  |  | user10 2 jobs |  |  |  |
|  |  |  | user21 1 jobs |  |  |  |
|  |  |  | user22 1 jobs |  |  |  |
|  |  |  | user9 1 jobs |  |  |  |
|  |  |  | user5 1 jobs |  |  |  |
|  |  |  | user4 1 jobs |  |  |  |
|  |  |  | user14 1 jobs |  |  |  |
|  |  |  | user12 1 jobs |  |  |  |
|  |  |  | user3 1 jobs |  |  |  |
|  |  |  | user20 1 jobs |  |  |  |

Fig. 9. A snapshot of our *JobViewer* interface in Grafana. Notice that usernames in the center list have been encoded for privacy reasons.

(from Slurm [35], a widely adopted job scheduler at the majority of open-science HPC sites, which exposes a RESTful API for conveniently accessing the accounting information), as depicted in Figure 10.

| time | memory_power | cpu- |  | memory_power | cpu | memory_power | cpu- |  | memory_power | cpu |  | memory_power | cpu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021-04-20 00:00:00 |  | 142 | 193 |  | 194 |  | 224 | 189 |
| 2021-04-20 00:20:00 |  | 142 | 195 |  | 192 |  | 216 | 193 |
| 2021-04-20 00:40:00 |  | 140 | 195 |  | 191 |  | 221 | 190 |
| 2021-04-20 01:00:00 |  | 141 | 195 |  | 191 |  | 216 | 189 |
| results |  |  |  |  |  |  |  |  |
|  |  |  | (a) |  |  |  |  |  |
| job id name | user id | user name | batch host | nodes | node co | cous | start time | end time |
| 5635835 H+_cyt_resub0 |  |  | cpu-25-23 | {cpu-25-23} |  | 128 | 1650469641 | 1650642441 |
| 5198865 C+Ura-1 |  |  | cpu-24-13 | (cou-26-9) | 1 | 128 | 1650385613 | 1650558413 |
| 5635836 H+_cyt_resub0 |  |  | CDU-25-31 | {cpu-25-31} | 11 | 128 | 1650469641 | 1650642441 |
| 5635986 INTERACTIVE |  |  | cpu-23-32 | {cpu-23-32} | 1 | 1 | 165047214( | 1650644940 |
| CADDOCO O |  |  |  |  |  | 4.00 | ACCOCCAL | V |
| job_id, name, user_id, user_name, batch_host, nodes, ncmt, cpus, start_time, end_time |  |  |  |  |  |  |  | V |

Fig. 10. Examples of input data for our*JobViewer* Grafana plugin: (a) Computing node health metrics and (b) Job scheduling data.

# VII. CONCLUSION

We have presented an application of human-centered computing in the case of HPC monitoring data. The visualization design bases on the idea of the bipartite graph that has prominence in scalability. The visualization can intuitively show an HPC system with resource allocation information and the system health states. We have demonstrated three use cases of historical data of an HPC cluster with 467 computing nodes to illustrate the proposed approach's usability. In addition, we have carried out a user study with three experienced experts in HPC monitoring. The results point out the strength of *JobViewer* and its weakness for further improvement in the future.

# Data Availability Statement

Our *JobViewer* web interface is implemented in Javascript using the D3.js library [36]. The source codes, data, as well as online demo are available on our Github project, at https://youtu.be/jskfR243wxQ and https://idatavisualizationlab.github.io/HPCC/jobviewer/index.html.

# VIII. ACKNOWLEDGMENTS

The authors acknowledge the High-Performance Computing Center (HPCC) at Texas Tech University [37] in Lubbock for providing HPC resources and data that have contributed to the research results reported within this paper. The authors are thankful to the anonymous reviewers for their valuable feedback and suggestions that improved this paper significantly. This research is supported in part by the National Science Foundation under grant CNS-1362134, OAC-1835892, and through the IUCRC-CAC (Cloud and Autonomic Computing) Dell Inc. membership contribution.

#### REFERENCES

- [1] Eugen Betke and Julian Kunkel. Real-time i/o-monitoring of hpc applications with siox, elasticsearch, grafana and fuse. In *International Conference on High Performance Computing*, pages 174–186. Springer, 2017.
- [2] Anthony Agelastos, Benjamin Allan, Jim Brandt, Ann Gentile, Sophia Lefantzi, Steve Monk, Jeff Ogden, Mahesh Rajan, and Joel Stevenson. Continuous whole-system monitoring toward rapid understanding of production hpc applications and systems. *Parallel Computing*, 58:90– 106, 2016.
- [3] Benjamin Schwaller, Nick Tucker, Tom Tucker, Benjamin Allan, and Jim Brandt. Hpc system data pipeline to enable meaningful insights through analysis-driven visualizations. In *2020 IEEE International Conference on Cluster Computing (CLUSTER)*, pages 433–441. IEEE, 2020.
- [4] Hao Zhang, Haihang You, Bilel Hadri, and Mark Fahey. Hpc usage behavior analysis and performance estimation with machine learning techniques. In *Proceedings of the International Conference on Parallel and Distributed Processing Techniques and Applications (PDPTA)*, page 1, 2012.
- [5] Ben Shneiderman and Aleks Aris. Network visualization by semantic substrates. *IEEE transactions on visualization and computer graphics*, 12(5):733–740, 2006.
- [6] Zhicheng Liu, Bongshin Lee, Srikanth Kandula, and Ratul Mahajan. Netclinic: Interactive visualization to enhance automated fault diagnosis in enterprise networks. In *2010 IEEE Symposium on Visual Analytics Science and Technology*, pages 131–138. IEEE, 2010.
- [7] Kazuo Misue. Drawing bipartite graphs as anchored maps. In *Proceedings of the 2006 Asia-Pacific Symposium on Information Visualisation-Volume 60*, pages 169–177, 2006.
- [8] Goldi Misra, Sandeep Agrawal, Nisha Kurkure, Sucheta Pawar, and Kapil Mathur. Chreme: A web based application execution tool for using hpc resources. In *International Conference on High Performance Computing*, pages 12–14, 2011.
- [9] David Carasso. *Exploring splunk*. CITO Research New York, USA, 2012.
- [10] Jon Stearley, Sophia Corwell, and Ken Lord. Bridging the gaps: Joining information sources with splunk. In *SLAML*, 2010.
- [11] Peter Zadrozny and Raghu Kodali. *Big data analytics using Splunk: Deriving operational intelligence from social media, machine data, existing data warehouses, and other real-time streaming sources*. Apress, 2013.
- [12] Nathan Debardeleben Hugh Greenberg. Tivan: A scalable data collection and analytics cluster. *The 2nd Industry/University Joint International Workshop on Data Center Automation, Analytics, and Control (DAAC)*, 2018.
- [13] Matthew L Massie, Brent N Chun, and David E Culler. The ganglia distributed monitoring system: design, implementation, and experience. *Parallel Computing*, 30(7):817–840, 2004.
- [14] Tobias Oetiker. Rrdtool. website, February 2017. Retrieved December 14, 2020 from https://oss.oetiker.ch/rrdtool/index.en.html.
- [15] Nagios Enterprises. Nagios. website, February 2017. Retrieved December 14, 2020 from https://www.nagios.org/.
- [16] Shajulin Benedict. Performance issues and performance analysis tools for hpc cloud applications: a survey. *Computing*, 95(2):89–108, 2013.
- [17] Amazon Inc. Amazon cloudwatch, 2012. http://aws.amazon.com/cloudwatch/. .
- [18] R. L. Warrender, J. Tindle, and D. Nelson. Job Scheduling in a High Performance Computing Environment. In *2013 International Conference on High Performance Computing Simulation (HPCS)*, pages 592–598, July 2013.
- [19] Mohammad I. Daoud and Nawwaf Kharma. A High Performance Algorithm for Static Task Scheduling in Heterogeneous Distributed Computing Systems. *Journal of Parallel and Distributed Computing*, 68(4):399 – 409, 2008.
- [20] Tommy Dang, Ngan Nguyen, and Yong Chen. Hiperview: real-time monitoring of dynamic behaviors of high-performance computing centers. *The Journal of Supercomputing*, 77, 10 2021.

- [21] Tommy Dang, Ngan Nguyen, Jon Hass, Jie Li, Yong Chen, and Alan Sill. The Gap between Visualization Research and Visualization Software in High-Performance Computing Center. In Christina Gillmann, Michael Krone, Guido Reina, and Thomas Wischgoll, editors, *VisGap - The Gap between Visualization Research and Visualization Software*. The Eurographics Association, 2021.
- [22] Ngan V. T. Nguyen, Jon Hass, and Tommy Dang. Timeradar: Visualizing the dynamics of multivariate communities via timeline views. In *IEEE 45th Annual Computers, Software, and Applications Conference, COMPSAC 2021, Madrid, Spain, July 12-16, 2021*, pages 350–356. IEEE, 2021.
- [23] Ngan Nguyen, Tommy Dang, Jon Hass, and Yong Chen. Hiperjobviz: Visualizing resource allocations in high-performance computing center via multivariate health-status data. In *2019 IEEE/ACM Industry/University Joint International Workshop on Data-center Automation, Analytics, and Control (DAAC)*, pages 19–24, 2019.
- [24] Grafana. The open platform for beautiful analytics and monitoring, 2019. https://grafana.com/.
- [25] G. Palmas, M. Bachynskyi, A. Oulasvirta, H. P. Seidel, and T. Weinkauf. An edge-bundling layout for interactive parallel coordinates. In *2014 IEEE Pacific Visualization Symposium*, pages 57–64, March 2014.
- [26] L. Wilkinson, A. Anand, and R. Grossman. Graph-theoretic scagnostics. In *Proceedings of the IEEE Information Visualization 2005*, pages 157– 164. IEEE Computer Society Press, 2005.
- [27] Tuan Nhon Dang, Anushka Anand, and Leland Wilkinson. Timeseer: Scagnostics for high-dimensional time series. *IEEE Transactions on Visualization and Computer Graphics*, 19(3):470–483, 2012.
- [28] Peter McLachlan, Tamara Munzner, Eleftherios Koutsofios, and Stephen North. Liverac: interactive visual exploration of system management time-series data. In *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems*, pages 1483–1492, 2008.
- [29] Dustin L Arendt, Russ Burtner, Daniel M Best, Nathan D Bos, John R Gersh, Christine D Piatko, and Celeste Lyn Paul. Ocelot: user-centered design of a decision support visualization for network quarantine. In *2015 IEEE Symposium on Visualization for Cyber Security (VizSec)*, pages 1–8. IEEE, 2015.
- [30] Tuan Nhon Dang, Nick Pendar, and Angus Graeme Forbes. Timearcs: Visualizing fluctuations in dynamic networks. In *Computer Graphics Forum*, volume 35, pages 61–69. Wiley Online Library, 2016.
- [31] Kumiyo Nakakoji, Akio Takashima, and Yasuhiro Yamamoto. Cognitive effects of animated visualization in exploratory visual data analysis. In *Proceedings Fifth International Conference on Information Visualisation*, pages 77–84. IEEE, 2001.
- [32] Miriah Meyer, Tamara Munzner, and Hanspeter Pfister. Mizbee: A multiscale synteny browser. *IEEE Transactions on Visualization and Computer Graphics*, 15(6):897–904, November 2009.
- [33] John A. Hartigan. *Clustering Algorithms*. John Wiley & Sons, Inc., New York, NY, USA, 99th edition, 1975.
- [34] Telemetry Streaming with iDRAC9, 2022.
- [35] Slurm Workload Manager, 2022.
- [36] Michael Bostock, Vadim Ogievetsky, and Jeffrey Heer. D3 datadriven documents. *IEEE Transactions on Visualization and Computer Graphics*, 17(12):2301–2309, 2011.
- [37] HPCC. High Performance Computing Center, 2022.

