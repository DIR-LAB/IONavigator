# DEFIO: A Software Defined Storage Network Architecture in HPC Environments

Wei Shi College of Computer National University of Defense Technology, China shiwei0060@gmail.com

Zhigang Sun College of Computer National University of Defense Technology, China sunzhigang@263.net

*Abstract*—**High performance computing (HPC) has witnessed a great boom of computing capability in recent years, however storage capacity fails to keep pace with that rapid growth, counteracting the benefits brought by higher computing power. Two dominating bottlenecks have been pointed out: firstly, Small-size IO requests fail to leverage the advantage of current distributed file systems and non-contiguous I/O access pattern induces more movement of disk heads. Secondly, coexistence of multi-tenant applications makes bandwidth guarantee more urgent while unfortunately, more complex. This article proposes a software defined storage network in HPC environments called DEFIO, providing a solution to reduce the adverse effect imposed by the above two bottlenecks, under the proposed architecture we establish several key technologies to solve performance and scalability issues in HPC storage networks.** 

*Keywords-component; HPC; storage; network; softwaredefined* 

# I. INTRODUCTION (HEADING 1)

Storage networks and distributed parallel file systems are pervasively deployed in HPC environments to provide high I/O bandwidth. However, explicit IO patterns and concurrency request from different tenant applications bring significant performance degradation of the I/O subsystem, and finally increasing the overall completion time of time-intensive applications such as whether prediction program. The main challenges that storage network confronts include:

# A. *Small and non-contiguous I/O access pattern*

Firstly, small IO requests cannot utilize the advantage of parallel and distributed file system such as Lustre [9], for the requested data fails to be partitioned into different strips, secondly, file system may establish caches in compute node to provide staging I/O capability, while small size I/O request has a poor cache hit rate, data has to be frequently dumped into disks as a result. Thirdly, non-contiguous I/O access pattern may induce more movement of disk heads, decreasing I/O capacity that storage servers can provide

Gaofeng Lv College of Computer National University of Defense Technology, China gaofenglv@163.com

Zhenghu Gong College of Computer National University of Defense Technology, China zhgong@163.com

## B. *Concurrent I/O access from multiple tenant applications*

HPC environments accommodate multi-tenant applications concurrently. Interference among different applications brings two adverse implications: one is the corruption of sequentiality: the sequential I/O requests from one individual application may be mixed with those from other applications at storage server side. One is the difficulty to guarantee bandwidth requirements of each tenants: there do not exist a mechanism to allocate I/O bandwidth resources for each distributed application.

Current researches have proposed solutions for tackling these two problems in isolation, this principle has implicit drawbacks: Resolving Problem A alone cannot prevent sequentiality disruption under concurrent application access. Considering Problem B alone will underutilize the storage capacity. In our proposed architecture, we demonstrate a software-defined storage architecture under which both problems are settled. The key innovation of this paper include:

- - The architecture design of DEFIO, which leverages existing facilities already deployed in modern HPC environments, including its forwarding layer and control layer design feature
- - A hierarchical storage design coupled with the SSD deployed in software defined gateways, aimed at improving I/O performance under the circumstance depicted in Problem A
- - A performance isolation mechanism under DEFIO which makes accurate and flexible control of large scale storage network realizable.

# II. RELATED WORK

Performance degradation under specific access pattern described in Problem A has drawn a lot of attention, MPI-IO specification [6] is made to utilize the potential parallelism and locality of parallel I/O requests, specifically, two phrase I/O and collective I/O can aggregate several small and nonsequential I/O requests into one large and consecutive request

978-1-4799-8937-9/15 $31.00 © 2015 IEEE DOI 10.1109/HPCC-CSS-ICESS.2015.223

![](_page_0_Picture_22.png)

[7]. Disk-side scheduling mechanisms overcome drawbacks of the FCFS method by reordering I/O requests in waiting queues to extract locality observed by the storage server side [8]. Direct I/O in Lustre file system bypasses local caching when issuing small I/O requests, eliminating cache replacement overhead. Recently SSD-based storage devices are introduced to store small files while keeping large files in hard disks in order to reduce small file access latency at an acceptable price. These solutions fail to function successfully under multitenants environments for all the endeavor may be ruined by the chaos along with concurrent storage accesses.

Bandwidth guarantee is more vital for service providers to execute SLAs (Service Level Agreement). However, current solutions put a lot of attention into bandwidth allocation in datacenter networks, these solutions stress on bandwidth guarantee either in static or dynamic manner, however, all of them are implemented at end hosts or edge switches, increasing the overhead of end hosts and fails to be employed in large scale systems such as HPCs. Besides, performance issue is not mentioned in the above solutions, resulting in poor storage I/O bandwidth and low storage resource usage.

HPC environments have storage network constructed by high performance and general-purpose hardware, favoring to establish software defined storage networks such as DEFIO. In chapter 3 we will discuss the architecture design of DEFIO, Chapter 4 introduces the key technologies under DEFIO aiming at resolving Problem A and B mentioned at Chapter 1.Chapter 5 introduces a prototype in which DEFIO is embedded. Chapter 6 concludes this paper.

## III. DEFIO ARCHITECTURE DESIGN

DEFIO is based on existing facilities deployed at HPCs. Being different from datacenters, mainstream HPC storage networks such as those in IBM BlueGenes and MilkyWay-2[2] are centered on ION (I/O Node) or gateways rather than hierarchical switches, Bluegene gateway functions as file I/O agent for computer nodes, gateways in MilkyWay-2 are equipped with high-performance general purpose processors, namely Intel Xeon with high-speed SSDs. All I/O requests issued by compute nodes will be processed through them before arriving at storage nodes. As a result, global network state statistics can be collected through gateways and explicit controls over I/O requests can be done by manipulations on gateways, Figure1 depicts the overall architecture of DEFIO.

![](_page_1_Figure_5.png)

Figure 1 the overall architecture of DEFIO

## A. *Global Component*

As can be seen in Figure1, software defined storage network has several essential components: the compute nodes as clients, the storage nodes as servers, and the gateway nodes which are responsible for transmitting I/O requests issued from clients to servers and file data fetched from servers to clients. Controller is a separate host (may coexist with MDS) responsible for implementing control plane functionality such as topology maintenance and monitoring of network states such as link utilization and flow statistics. High speed networks such as 10Gb Ethernet and Infiniband are utilized to connect different components.

## B. *Hirarchical Data Plane*

Hierarchical data plane are designed to provide hostgranularity forwarding service and tenant level QoS enforcement at different locations.

There exists light-weight data plane implementation on each compute node, which functions as simply a rate limiter and router for local traffic, the rate limiter provide a precise bandwidth control compared with traditional TCP mechanism and the router forwards packets based on specific routing strategies. Both the two functions are implemented in network drivers with no tuning at file system or application required.

Most data plane functions are implemented at gateway nodes in which multiple queues are established to control the I/O behavior of each tenant flow. For example, in gateway1 all flows belongs to Tenant A are queued by Q1 and flows belong to Tenant B are queued by Q2, gateway 2 also has the similar functionality. Monitoring and manipulating of all tenants can be done through statistics and operations on distributed queues. The complexity of controlling is determined by the number of tenants and gateways rather than the number of hosts, which is the reason why DEFIO can be practical on large systems such as HPCs.

Only gateway data plane stores flow statistic and monitors link utilization rate and shares them with the controller, currently there exists multiple SDN data plane standards, of which Openflow is the most typical one, Openvswitch is an implementation of Openflow in commodity hardware which can be directly leveraged to fulfill data plane functionalities.

#### C. *Control Plane Functionality*

In the case of bandwidth allocation among tenants, the main tasks of control plane is to collect information such as the I/O behavior of each tenant and available service capacity of resources, then gateway rules are generated based on the realtime information and then issued by the controller to each gateway. However, rate limiting merely on gateways fails to function for the queue will finally be overflowed by the incoming requests. DEFIO resolves this problem by two-phrase control mechanism: the first control stage happens between the controller and gateways which regulates the bandwidth requirements that gateways have to abide by; the second stage happens between gateways and clients during which explicit rate limit requirements conveyed by percentage are sent to end host data planes with piggyback packets.

## *D. I/O Access Procedure under DEFIO*

I/O access procedure under DEFIO is quite different from that in regular distributed file systems. The key design goal of DEFIO is that no packet will transmit between data plane and control plane. Because file layout information locates at MDS (Metadata Server) in distributed file systems, clients have to send an inquire request to get file location information before issuing actual I/O requests. In DEFIO, the first inquire packet will carry tenant-bonded QoS demand in terms of detailed parameters inside, controller in MDS will correspondingly establish a sub graph which contains explicit gateway nodes and storage nodes that will serve the tenant. Then initial data plane rules will be built in those gateway nodes according to tenant demand. After all these are done, MDS will return file metadata and gateway message to the client node. And the following inquiries from the same tenant will get an instant response informing clients the routing information. After this clients can issue actual I/O requests and gateway will process them based on the pre-built rules, as a result packet do not need to be sent to the controller and the latter will not become a bottleneck when implementing software defined functions.

## IV. KEY TECHNOLOGIES OF DEFIO

Under the DEFIO architecture described in Chapter 3, we build three key technologies to resolve performance degradation problem under small-size file access and guarantee bandwidth for multiple tenants.

## A. *File Caching through gateway SSD*

File caching is implemented as a method to accelerate specific file accessing. However, for cost consideration it is impossible to cache all files in high speed media. Practically small files are stored in embedded SSD and large files are stored in traditional hard disks, in this way long access latency can be eliminated when accessing small files and hard disk can leverage its advantage on volume.

However, cache replacement strategies are still open issues, software defined gateways can implement flexible caching policies in real time, including choosing when to cache, what to cache and when to dump data into disks according to file size and state of hard disk arrays. Caching small files alone is not able to resolve performance issues of hard disk storage because concurrent I/O access from multiple applications will disrupt sequentiality of individual application. I/O phrase overlapping is the root cause of concurrent I/O access, it is of great importance to eliminate I/O phrase overlapping by delaying and redirect I/O requests of some applications into gateway SSDs. Then the total caching strategy is clear: first, gateways will check the sizes of I/O accesses, small file access will be cached into SSDs and when target disk is free to use, data in SSD will be write back into hard disks. Another scenario of caching is to avoid I/O phrase overlapping, in this situation some applications have to wait until the end of I/O phrase of other applications.

## B. *Bandwidth Guarantee Through Hierachical Controller*

Previous researches such as IOFlow[1] has already proposed its software-defined solution to make bandwidth guarantee more feasible in small datacenters, however, IOFlow brings too many hierarchical layers or data planes at endpoints and needs to establish multiple queues in each data plane layers. In order to perform bandwidth guarantee, the centralized controller need to communicate with each queue to collect their statistic and make new rules if bandwidth guarantee is broken. This method has poor scalability when applied in large systems for there is massive communication between data plane and control plane which overloads the controller, resulting in unacceptable delay and complexity.

In this paper the proposed bandwidth guarantee is fulfilled through establishing a hierarchical data plane locating at software defined gateways and end hosts, the gateway component is responsible for collecting statistic for each tenant, for example if tenant X has a fixed bandwidth guarantee that its total write bandwidth is set to N bps, then at each gateway a statistic is assigned for write bandwidth of tenant A and root controller collects all statistics from software defined gateways to make new rules if bandwidth guarantee is broken, rule enforcement is done at end component, here if aggregate write bandwidth of tenant A is 2Nbps, then the software defined gateway components will send a feedback packet informing each host that communicate with it to halve its request rate. The actual effect is that gateways play as the role of the controllers of end hosts, the root controller has the only expenditure for collecting statistics in all software defined gateways, the complexity is only proportional to the number of gateways (G) and the number of tenants (T), the exact value can be concluded as O (T*G) which is much smaller than the O (H) complexity in the IO-Flow implementation. And the communication amount between data plane and control plane is sharply decreased by replacing it with communication between leaf controllers and root controller. Therefore our method can be applied in large scale systems and has improved performance, low latency and excellent scalability compared with previous researches.

# V. DISCUSSION

I/O performance has been a bottleneck factor to improve the HPC system performance. However, as computing power in HPC centers continues to boost, I/O performance, duo to low speed disk and concurrent access, do not get the expected rapid growth. The appearance of SSD leads a promising way to fill this performance gap[3], while high price/IOPS ratio makes an obstacle for SSD to replace disk array completely. As a result hierarchical storage is currently a fashionable method to make compromise between performance and cost. How to make best use of SSD is introduce several open issues in HPC storage networks, of which choosing a proper caching policy is of utmost importance. We believe that implementing flexible caching policy can achieve different targets in different scenario, which need support of software defined storage.

Besides, QoS enforcement in data center and HPC environments becomes a hot spot in recent years. However, different application has different demands, no comprehensive solution can cover all requirements. For example researches propose bandwidth guarantee in different granularity , for example per host/VM and per tenant granularity in order to accommodate various user demands[4][5], while as datacenter and HPC environments begin to host more and more applications of different features, single QoS policy enforcement cannot provide sufficient resource allocation functionality in this background.

SDN is a promising architecture that completely decouples control plane and data plane, which makes updating network service with legacy network devices possible. However, most researches cast their attention to QoS enforcement in communication among compute nodes. Only a few researches focus on resolving storage network problems, of which IOflow is the most typical one deployed in Windows Azure datacenter. However IOflow does not deploy any SDN dataplane in intermediate nodes, partly because switch-centered architecture of data center. However in HPC environments ION/gateway nodes are built via commodity hardware, offering an opportunity to deploy SDN data plane.

#### VI. CONCLUSION

DEFIO is a software defined storage network architecture deployed at HPC environments which centers software defined gateways, it is practical in large scale systems for no I/O request will be passed between control plane and data plane, under this architecture we develop key technologies to solve performance issue under small-file accessing and bandwidth guarantee problem under concurrent application, through gateway file caching and hierarchical controller design. Future work will focus on the implementation of the above key technologies and we are also interested in fulfilling storage load balancing or eliminating storage hotpot under DEFIO.

#### VII. REFERENCES

[1] Thereska, Eno, et al. "Ioflow: A software-defined storage architecture." Proceedings of the Twenty-Fourth ACM Symposium on Operating Systems Principles. ACM, 2013.

[2] Liao, Xiangke, et al. "MilkyWay-2 supercomputer: system and application." Frontiers of Computer Science 8.3 (2014): 345-356.

[3] Welch, Brent, and Geoffrey Noer. "Optimizing a hybrid SSD/HDD HPC storage system based on file size distributions." Mass Storage Systems and Technologies (MSST), 2013 IEEE 29th Symposium on. IEEE, 2013.K. Elissa, "Title of paper if known," unpublished. 

[4] H. Ballani, P. Costa, T. Karagiannis, and A. Rowstron. Towards predictable datacenter networks [C]. In Proc. of SIGCOMMÿ11, 242-253, 2011.

[5] Terry L, George V. NetShare: Virtualizing Bandwidthwithinthe Cloud [R]. 2010.

[6] Thakur, Rajeev, William Gropp, and Ewing Lusk. "On implementing MPI-IO portably and with high performance." Proceedings of the sixth workshop on I/O in parallel and distributed systems. ACM, 1999.

[7] Isaila, Florin, et al. "Integrating collective I/O and cooperative caching into the Clusterfile parallel file system." Proceedings of the 18th annual international conference on Supercomputing. ACM, 2004.

[8] Bruno, John, et al. "Disk scheduling with quality of service guarantees." Multimedia Computing and Systems, 1999. IEEE International Conference on. Vol. 2. IEEE, 1999.

[9] Braam, Peter J. "The Lustre storage architecture." (2004).

