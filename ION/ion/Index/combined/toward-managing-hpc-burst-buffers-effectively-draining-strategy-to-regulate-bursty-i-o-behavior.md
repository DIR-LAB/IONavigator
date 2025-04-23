# Toward Managing HPC Burst Buffers Effectively: Draining Strategy to Regulate Bursty I/O Behavior

Kun Tang∗, Ping Huang∗, Xubin He∗, Tao Lu†, Sudharshan S. Vazhkudai‡, and Devesh Tiwari§

∗Temple University †New Jersey Institute of Technology ‡Oak Ridge National Laboratory §Northeastern University

*Abstract*—HPC (high-performance computing) applications usually show bursty I/O behaviors. In order to expedite the applications, permanent storage systems are usually provisioned to serve such I/O bursts. Approaching the era of exascale computing, non-volatile RAM is introduced as burst buffers, to absorb the bursty bulk data and relax the I/O provisioning requirement of the permanent storage systems. However, without judiciously draining the burst buffers, I/O bursts are passed down to the underlying storage systems, which causes severe I/O contention issues.

In order to minimize the I/O provisioning requirement and resolve the issues caused by I/O bursts, we propose a proactive draining scheme to manage the draining process of distributed node-local burst buffers. In addition, we develop an I/O provisioning model to predict the minimized I/O provisioning requirement for permanent storage systems. Evaluation results show that applying the proactive draining scheme largely relaxes the I/O provisioning requirement while preserving the I/O performance of underlying storage systems.

#### I. INTRODUCTION

In high-performance computing (HPC), scientific applications usually show periodic bursty I/O behaviors [1]. In the computation phase, scientific applications rarely perform storage I/O operations. Analysis files and checkpoint files are written intensively to the permanent storage system at the end of every computation segment. At machine level, various applications run simultaneously. The I/O phases of different applications overlap with each other, which leads to even higher I/O peaks. Permanent storage systems are typically provisioned to serve those I/O peaks, in order to minimize I/O overheads between consecutive computation segments. However, this leads to resource underutilization between consecutive I/O peaks. Taking the former supercomputer Intrepid at Argonne National Laboratory as an example, the aggregate I/O throughput is lower than one-third of the peak I/O bandwidth for 99% of the time [2][3].

The ever-increasing computing capability exerts escalating I/O demands on the storage systems. In order to boost I/O performance, burst buffers are introduced to absorb the bulk data and expedite I/O requests [4]. For example, supercomputer Cori at National Energy Research Scientific Computing Center is equipped with an off-node shared burst buffer [5]. In addition, future supercomputer Summit at Oak Ridge National Laboratory will have non-volatile RAM serving as node-local burst buffers upon delivery [6]. A burst buffer is a layer of high-performance storage, which sits between main memory and permanent storage systems. HPC applications dump data rapidly to burst buffers which asynchronously drain data to the underlying permanent storage system.

Burst buffers can absorb I/O bursts, thus providing opportunities to relax the provisioning requirement on I/O bandwidth of the underlying permanent storage system. For example, with the introduction of high-performance burst buffers, the permanent storage system of the next-generation supercomputer Summit [6] is provisioned to have the same bandwidth (1 TB/s) as the storage system of supercomputer Titan [7]. Unfortunately, if not carefully designed, the burst buffer draining process still causes similar I/O bursts on the permanent storage systems [4]. In this situation, the permanent storage system still needs to be provisioned for I/O performance rather than storage capacity. Forcing the reduction in the I/O provisioning of the permanent storage system causes the following issues. First, the storage system suffers from severe I/O contention and long tail latency at I/O peaks. This directly affects the read and restart performance of scientific applications, data analysis tasks, data visualization tasks, and interactive user activities on the storage system. Secondly, the burst buffer draining speed is also impacted around the I/O peaks, which causes data to accumulate in the burst buffers. If the burst buffer capacity is exhausted, application I/O performance will get impacted. Finally, it is hard to determine the minimal I/O provisioning requirement of the permanent storage system.

In order to relax the I/O provisioning requirement and resolve the aforementioned issues associated with bursty I/O behaviors, we propose a proactive burst buffer draining scheme to regulate the bursty I/O behaviors and relax the I/O provisioning requirement. Based on the proactive burst buffer draining scheme, we propose a storage I/O provisioning model to predict the I/O provisioning requirement for the permanent storage system. We evaluate the proactive burst buffer draining scheme and show that it flattens I/O peaks and maintains the I/O performance for other clients sharing the storage system. We also validate the I/O provisioning model based on realsystem traces and simulation, and perform sensitivity studies on model parameters. Furthermore, we demonstrate that applying the proactive burst buffer draining scheme achieves nearmaximal reduction in storage I/O provisioning requirement for representative scientific applications. We note that the Cray DataWarp I/O accelerator [8] also relieves the burden of the underlying storage system, it targets centralized burst buffers rather than distributed node-local burst buffers. However, our strategy can potentially be leveraged by other researchers to be applied in conjunction with Cray's Data Warp infrastructure to further improve the performance of the system [8].

The rest of this paper is organized as follows. We discuss the background and motivation in Section II. In Section III, we introduce the design of the proactive burst buffer draining scheme. The I/O provisioning model is introduced in Section IV. We present the validation and evaluation results in Section V. In Section VI, we discuss the proactive burst buffer draining scheme in various aspects. Section VII summarizes related work and Section VIII concludes the paper.

# II. BACKGROUND AND MOTIVATION

In this section, we first describe the infrastructure of HPC storage systems. Then, we discuss the HPC I/O characteristics and the motivation of this paper.

![](_page_1_Figure_4.png)

Fig. 1: Storage infrastructure hosted at Oak Ridge National Laboratory [7].

We use the OLCF (Oak Ridge Leadership Computing Facility) Spider storage system [9] as an example to describe the storage infrastructure. As illustrated in Fig. 1, the computing resources and permanent storage system are connected through a scalable I/O network consisting of InfiniBand switches. There are about 26,000 nodes mounted on the Spider storage system, where supercomputer Titan takes up more than two thirds of the nodes [10]. The center-wide storage system is shared by multiple computing resources, including supercomputer Titan, analysis cluster Rhea, visualization cluster Everest, etc. To meet the increasing data-sharing requirements, it is practical for HPC facilities to employ a center-wide storage system. The storage system at OLCF experienced the transition from a machine-exclusive model to a center-wide, data-centric model in 2005 [11]. On the storage side, the Lustre-based parallel filesystem runs on 288 Object Storage Servers (OSS). A total of 2,016 Object Storage Targets (OST) are connected to DataDirect Networks (DDN) SFA12K-40 RAID controllers. Each OST consists of 10 hard drives as a RAID6. An I/O monitoring tool regularly polls the DDN controllers and stores the I/O statistics (e.g., throughput, IOPS, etc.) into a database [12]. On the next-generation supercomputer Summit, nodelocal non-volatile memory is introduced as burst buffers.

Fig. 2 shows a 24-hour write trace of the Spider storage system. We observe that, for most of the times, aggregate write throughputs are below 10 GB/s. However, for the other times, aggregate write throughputs are above 10 GB/s and even larger than 20GB/s. As demonstrated by the I/O log, mostly, the I/O load is much lower than what the storage system can provide. However, the storage system is provisioned in order to provide sufficient bandwidth to the few I/O peaks. If a storage system is provisioned to serve I/O peaks, it is underutilized for the time between I/O peaks. Although modern systems exploit various buffers to serve the I/O peaks, such peaks still exist on the permanent storage system without judiciously draining the buffers [4].

![](_page_1_Figure_8.png)

Fig. 2: One-day I/O (write) log for Spider storage system hosted at Oak Ridge National Laboratory.

HPC applications are known for periodic bursty I/O behaviors [1]. Taking the Community Earth System Model (CESM) as an example, climate data are stored to the permanent storage system per month simulation. Checkpoints are taken after every 3-month simulation. As illustrated in Fig. 3a, both application outputs and checkpoints are periodic and bursty. At machine level, various applications run simultaneously, which makes I/O peaks from different applications overlap with each other and create even higher peaks, as shown in Fig. 2.

Approaching exascale computing, the storage I/O is expected to have an O(100) increase comparing with petascale systems [13][14][15][16]. We continue using the OLCF resources as an example. In the current petascale system, the Spider storage system consumes 400 KW power [7], and the peak power consumption of supercomputer Titan is 9 MW [17]. In an exascale system with a power limit of 20 MW [18], it would consume a considerable amount of the power budget to provision for the O(100) increase in storage I/O. In order to expedite the storage I/O performance under power constraints, burst buffers are introduced to absorb the bursty bulk data and relax the I/O provisioning requirement of the underlying permanent storage systems. However, without judiciously draining the distributed burst buffers, I/O bursts still exist in the underlying storage systems [4]. Since the aggregate bandwidth of storage system is lower than the burst buffers, I/O bursts are reduced passively at the storage system. As a result, the I/O contention is exacerbated due to underprovisioning at the original I/O peaks from the applications.

![](_page_2_Figure_0.png)

Fig. 3: Fig. 3a shows a sample I/O (write) trace from a 15-month CESM simulation on supercomputer Titan with component sets F 2000 and resolution f19 f19. This smallscale sample run is used to illustrate the I/O periodicity of scientific applications. Fig. 3b shows the aggregate I/O throughput for increasing number of applications on 4 OSTs.

The read and write performance of the permanent storage systems suffer from the severe I/O contention at the I/O peaks.

We run a real-system emulation to illustrate the I/O contention issues on under-provisioned storage systems. When running multiple applications on shared storage resources, under-provisioning can lead to severe resource contention. When the number of applications sharing the same storage resources is relatively small, running more applications can achieve higher aggregate I/O throughput. As illustrated in Fig. 3b, when the number of applications increases from 1 to 3, the aggregate I/O throughput increases from 950 MB/s to 1700 MB/s. However, when the number of applications running on shared storage resources keeps growing, the aggregate I/O throughput drops significantly. As shown in Fig. 3b, when the number of applications increases from 3 to 16, the aggregate I/O throughput decreases from 1700 MB/s to 250 MB/s. Running more applications than the serving capability of the storage system (i.e., the storage system is under-provisioned) causes severe resource contention. As a result, the performance of the storage system is degraded severely (85% degradation as shown in Fig. 3b).

In this paper, we aim to minimize the storage I/O provisioning requirement and resolve the problems associated with I/O peaks utilizing the periodicity attribute of HPC I/O. As discussed in Fig. 3a, HPC applications dump data periodically to burst buffers. An intuitive strategy is to reactively flush the data as they arrive at burst buffers, known as reactive draining [19]. Instead of employing the reactive draining strategy, we propose to drain the data proactively to the permanent storage system, in order to flatten I/O peaks in the storage system. In the next section we show that careful design of controller for proactive draining is critical to avoid performance degradation. Efficient design of controller for proactive draining makes this scheme simple yet effective, as shown by our evaluation.

## III. PROACTIVE BURST BUFFER DRAINING SCHEME

The proactive burst buffer draining scheme exploits the I/O periodicity. Since application I/O performance mainly relies on the burst buffer instead of the permanent storage system, the proactive burst buffer draining scheme can scatter the I/O draining process within the I/O interval while not impacting the application I/O performance. As illustrated in Fig. 4, applications dump data periodically and burst buffers perform draining in an asynchronously manner. Using reactive draining, as shown in Fig. 4a, burst buffer flushes data quickly, which passes the I/O bursts on to the underlying storage system. By comparison, using proactive draining as illustrated in Fig. 4b, data are divided into small blocks and draining requests are dispersed evenly across the entire computation and I/O period. Consequently, I/O bursts stop at the burst buffer layer.

![](_page_2_Figure_7.png)

(b) Proactive burst buffer draining

Fig. 4: An illustration of reactive and proactive burst buffer draining. Arrows represent application I/O and burst buffer draining requests.

In a HPC storage system, OSTs are typically assigned to applications in a round-robin manner. As illustrated in Fig. 5a, OST 1 to 8 are assigned to application one and OST 9 to 16 are assigned to application two. Each file of application one is striped across 4 OSTs and each file of application two is striped across 2 OSTs. In reactive burst buffer draining, burst buffers flush data reactively to the underlying permanent storage system when data become available in burst buffers. After burst buffers get the assigned OSTs, the OSTs are appended to the waiting queue. Using proactive burst buffer draining, in this example, each file is divided into two segments, as illustrated in Fig. 5b. The burst buffer draining controller drains the first segment of each file, and then drains the second segment. Burst buffers issue draining requests to the assigned OSTs for an extended time period. The draining segments arrive at the same group of OSTs periodically. As shown in Fig. 5b, the draining segments of application two are interleaved with application one on the same OSTs. In proactive draining, segment is the basic scheduling and draining unit. I/O requests within draining segments of different applications do not overlap with each other. Otherwise, sequential I/O requests from multiple

![](_page_3_Figure_0.png)

Fig. 5: An comparison between reactive and proactive burst buffer draining. Arrows represent burst buffer draining paths of different files and segments. The burst buffers drain 2 files of application one with a stripe count of 4, and drain 4 files of application two with a stripe count of 2. Using proactive draining, each file is divided into 2 segments which are drained sequentially.

applications interleave with each other and turn into random I/O requests, causing request contention on OSSs and resource contention on OSTs.

![](_page_3_Figure_3.png)

Fig. 6: An illustration of the data partition for proactive burst buffer draining. Layers SION, OSS, and DDN are not plotted for simplicity.

We use application one in Fig. 5b as an example to illustrate the data partition of the proactive burst buffer draining. As shown in Fig. 6, burst buffers drain nf files (application output or checkpoint) to the permanent storage system. Each file is divided into N segments and each segment is divided into Nio stripes. The entire file is divided into Sio stripes, and is striped across nost OSTs. The file size is S and the stripe size is ss. The relationship between these parameters is defined in Eq. 1.

$$N=\frac{S_{io}}{N_{io}}=\frac{S}{N_{io}\times s_{s}}\tag{1}$$

For node-local burst buffers, each compute node has a burst buffer draining controller. In each node, the draining controller calculates the application I/O interval based on the time difference between the start of application and the start of data dump. From the perspective of a specific group of OSTs, there is a set of applications sharing them. In order to coordinate the draining process of different applications and avoid contention across applications on the shared OSTs, the proactive burst buffer draining controllers need to calculate the maximum time span for draining segments of different applications. Then, the draining controller splits the data into appropriate draining segments accordingly, and drains the segments periodically. Draining segments from different applications arrive at the shared OSTs periodically, interleaving with each other. The OSS keeps a map for each group of OSTs to record the application set. Every time a new application is added into the set or an existing one is removed from the set, the operation is registered in the related map. The proactive burst buffer draining controller regularly polls the map and updates the maximum time span for the draining segments.

#### IV. I/O PROVISIONING MODEL

In Section III, we have discussed the design of the proactive burst buffer draining scheme. Based on the scheme, we propose the I/O provisioning model to calculate the minimized I/O provisioning requirement for permanent storage systems. Symbols used in the model are listed in Table I.

TABLE I: Symbols and Definitions

| Symbols | Definitions |
| --- | --- |
| T | I/O interval of checkpoint or analysis dump |
| P(r) | I/O throughput of reactive burst buffer draining |
| r | ratio between I/O time and I/O interval |
| B | proactive draining throughput without interference |
| B | proactive draining throughput with interference |
| S | application data size per file |
| Sio | number of application data stripes per file |
| ss | data stripe size |
| nost | number of OSTs to stripe over |
| N | number of draining segments per file |
| Nio | number of data stripes per draining segment |
| t | time of a draining segment per file |
| t | hard drive positioning time |
| nf | number of application files |
| Si | application data size of the ith file |
| Ni | number of draining segments of the ith file |
| ti | time of a draining segment of the ith file |
| na | number of applications sharing common OSTs |
| T(x) | the xth application I/O interval |
| S(x) | application data size of the xth application |
| N(x) | number of draining segments of the xth application |
| t(x) | time of a draining segment of the xth application |

When burst buffers perform draining reactively, the draining I/O throughput is similar to the application I/O throughput, if the storage system is provisioned to an adequate degree. I/O throughput is defined as the ratio between application data size and I/O time. If the storage system is provisioned to allow r fraction of application computation time to perform I/O operations, the reactive draining throughput is defined as Eq. 2.

$$P_{(r)}=\frac{\sum_{i=1}^{n_{f}}S_{i}}{r\times T}\tag{2}$$

In proactive burst buffer draining, data are divided into draining segments which are dispersed evenly over the I/O interval (T). The burst buffer draining throughput is controlled through adjusting the number of I/O requests issued each time (i.e., the size of the draining segments). Without considering the interference of other applications, the proactive draining throughput is defined in Eq. 3.

$$B=\sum_{i=1}^{n_{f}}\frac{S_{i}}{N_{i}\times t_{i}}\tag{3}$$

In a throughput-oriented storage system, the aggregate I/O throughput normally increases as the number of concurrent I/O requests increases. In order to quantify this relationship, we perform a regression analysis based on the simulation results. We employ the Disksim [20] simulator with the validated disk parameter set "Seagate Cheetah 15k.5". The simulation shares the real-system emulation settings in Section V, except that we configure each disk array to have 9 disks as a RAID5, which has the same number of non-parity disks (8 disks per OST) as the emulation settings. In order to quantify the relationship between number of concurrent I/O requests and aggregate I/O throughput, we also employ a SSD model [21] created by Microsoft Research in the regression analysis.

In the I/O provisioning model, the number of data stripes per draining segment (Nio) has upper and lower bounds. The lower bound is calculated based on device block size and data stripe size. The device block size is 512 bytes in the simulation settings. The product of Nio and data stripe size should be larger than the product of device block size and the number of non-parity disks. The lower bound of Nio is 12 in the simulation settings. Concerning the upper bound, when Nio grows beyond the upper bound, aggregate I/O throughput keeps steady and the OSTs become saturated.

![](_page_4_Figure_6.png)

Fig. 7: Aggregate draining I/O throughput under various data stripe counts on 4 OSTs.

TABLE II: Coefficients for Regression Analysis

| Coefficients | MAX HDD 1 MB | HDD 1 MB | HDD 2 MB | SSD |
| --- | --- | --- | --- | --- |
| a | 0.585 | 0.693 | 0.648 | 0.552 |
| b | 1.044 | 0.163 | 0.688 | 3.653 |

As shown in Fig. 7, the aggregate I/O throughput reaches a plateau, as the number of data stripes gets larger. Concerning HDD as storage resources, beyond an upper bound of Nio, the aggregate I/O throughput remains steady at 4.0 GB/s. When data stripe size equals to 1 MB and 2 MB, the upper bounds of Nio are 1536 and 768 respectively. When it comes to SSD, the upper bound reduces significantly to 100 and the aggregate I/O throughput remains steady around 5.5 GB/s beyond the upper bound of Nio. In the proactive burst buffer draining scheme, we propose to drain the application data in a number of segments with smaller Nio, in order to reduce I/O peaks. Therefore, we only consider the range between the upper and lower bounds of Nio. We find that the I/O throughput trend can be captured by natural logarithm functions, as illustrated by the solid lines in Fig. 7. The R-squared values of regression functions are above 0.997 for HDD and are above 0.981 for SSD, which indicate a statistically sound fit. According to the regression analysis, the relationship between the number of data stripes (Nio) and aggregate I/O throughput per file (B- ) can be expressed as Eq. 4.

$$B^{\prime}=\frac{S}{N\times t}=a\times\ln(N_{io}/n_{ost})+b\tag{4}$$

Coefficients a and b vary across different storage settings, which are listed in Table II. Combining Eq. 1 and Eq. 4, time of a draining segment per file (t) can be expressed as Eq. 5.

$$t=\frac{N_{io}\times s_{s}}{a\times\ln(N_{io}/n_{ost})+b}\tag{5}$$

According to Eq. 5, the time of a draining segment of the ith file (ti) is independent of the file size (Si), but is dependent on the number of data stripes per draining segment (Nio).

In the permanent storage system, applications request and release OSTs in a round-robin manner. After applying the proactive burst buffer draining scheme, draining segments arrive periodically for an extended period after the OSTs are released, making the OSTs being shared by multiple applications. Sequential draining segments from multiple applications interleave and interfere with each other, which incurs notably large disk positioning time in front of each draining segment. Disk positioning time ( t ) consists of seek time and rotational latency. It is essential to consider the impact of disk positioning time in the context of multi-applications, especially with small draining segments. When burst buffers perform proactive draining as illustrated in Fig. 5b, considering the interference across applications, the I/O throughput is defined in Eq. 6.

$$\tilde{B}=\sum_{i=1}^{n_{f}}\frac{S_{i}}{N_{i}\times(t_{i}+\overline{t})}\tag{6}$$

Between each of the N draining segments, the storage resources are utilized by the other applications. Since draining segments only append to each other instead of breaking into each other, there exists extra hard drive positioning time t at the beginning of each segment. Hard drive positioning time is dominated by the seek time as rotational latency remains constantly small. Seek time can be expressed as a function of seek distance [22][23]. Each of the N segments has a distinct hard drive positioning time depending on the seek distance. In order to simplify the I/O provisioning model, we propose an aggressive strategy and a conservative strategy for calculating the draining I/O throughput B. When the storage system is shared with latency-sensitive applications (e.g., data analysis and visualization), the conservative strategy should be used in order to preserve the available I/O bandwidth for the other applications. Otherwise, the aggressive strategy can be used to reduce the I/O provisioning requirement.

- Using the aggressive strategy, t is the average positioning time for all N segments. In this case, parameters a and b in Eq. 4 are derived from the average I/O throughput.
- Under the conservative strategy, t is the minimum positioning time among all N segments. Parameters a and b are measured based on the maximum I/O throughput.

The draining I/O throughput is reduced passively by random I/O requests, due to extra disk positioning time between draining segments. Therefore, to achieve draining I/O throughput B, the permanent storage system is actually provisioned at bandwidth B. According to Eq. 4, when the size of draining segments (Nio) decreases, draining I/O throughput decreases. In contrast, the gap between B and B grows larger as Nio decreases.

On shared storage resources, the minimum I/O throughput is constrained by the minimum draining throughput of each client. The minimum draining throughput of a client is defined as the ratio between data size (S(x)) and I/O interval (T(x)). When multiple clients share the storage resources, the draining throughput of client x should be larger than the aggregate minimum throughput of all clients, in order to let clients finish draining within their I/O intervals, as defined in Inequality 7.

$$\frac{S_{(x)}}{N_{(x)}\times(t_{(x)}+\overline{t})}\geq\sum_{x=1}^{n_{a}}\frac{S_{(x)}}{T_{(x)}}\tag{7}$$

Using smaller draining segments (Nio) leads to lower draining throughput and longer draining time. On shared storage resources, if one client drains data at lower throughput and takes longer time, the other clients will have to perform draining at higher throughputs due to shortened time slices. Therefore, in order to minimize the overall I/O throughput, all clients sharing the same group of OSTs should adopt the same size of draining segments. According to Inequality 7, the minimum segment size (Nio) should satisfy the following inequality.

$$\frac{1}{a\times\ln(N_{io}/n_{ost})+b}+\frac{\overline{t}}{N_{io}\times s_{s}}\leq\frac{1}{\sum_{x=1}^{n_{a}}\frac{S_{(x)}}{T_{(x)}}}\tag{8}$$

Every time a new application is assigned to a group of OSTs or an existing application completes its execution, the maximum time span of each client changes accordingly. The unified number of data stripes per draining segment (Nio) is updated based on inequality 8, and each client adopts the updated Nio to drain data.

## V. EVALUATION

We perform the evaluation based on emulation, simulation, and model-driven methods. In Subsection V-A, we evaluate the proactive burst buffer draining scheme and compare against the reactive burst buffer draining scheme. In Subsection V-B, first, we validate and evaluate the I/O provisioning model. Then, we evaluate the model with leadership applications.

We evaluate and compare the proactive draining scheme and reactive draining scheme based on real-system emulation on the OLCF Spider storage system. I/O statistics are collected at both application level and DDN RAID controllers. In the emulation, benchmark IOR [24] is used to emulate 12 applications with random start offsets and various I/O intervals. We employ 4 OSTs (40 hard drives) to perform the emulation since the default stripe count is 4. In order to keep the same ratio between compute nodes and OSTs as the entire Spider storage system, we utilize 36 compute nodes in the emulation. Each application runs on 3 compute nodes (48 processors). To be noted that, we use the emulation to illustrate and compare the aggregate I/O bandwidth and system I/O performance under different burst buffer draining schemes. The comparison results also apply to the other OSTs in the entire system. Therefore, the emulation scale is sufficient for the illustration of and comparison between different draining schemes.

## *A. Burst Buffer Draining Schemes*

First of all, we employ a real-system emulation to demonstrate how the proactive burst buffer draining scheme proactively flattens the aggregate I/O peaks for all applications. Throughput data are collected from the DDN RAID controllers of the Spider storage system. Emulation results are shown in Fig. 8. Comparing Fig. 8a and Fig. 8c, we observe that without applying the proactive burst buffer draining scheme, I/O peaks drop from 1300 MB/s to 800 MB/s in a passive manner when storage provisioning is halved from 4 OSTs to 2 OSTs. This indicates that, using 2 OSTs, applications have higher I/O provisioning requirement and the storage system is overloaded near the original I/O peaks. In contrast, comparing Fig. 8a and Fig. 8b, when applying the proactive burst buffer draining scheme, I/O peaks are flattened at 500 MB/s in an active manner. When storage provisioning is halved from 4 OSTs to 2 OSTs, as shown in Fig. 8d, I/O peaks remain steady around 500 MB/s and the storage system is underloaded, whose peak bandwidth can be as high as 800 MB/s according to Fig. 8c. From the comparison, we observe that decreasing the I/O provisioning reduces the I/O bursts passively, when burst buffers drain data reactively. This usually causes severe I/O contention issues among draining processes and other clients sharing the storage system. However, applying the proactive

![](_page_6_Figure_0.png)

Fig. 8: Aggregate bandwidth for all 12 applications under various storage configurations.

burst buffer draining scheme actively flattens the I/O bursts, which in return preserves the available bandwidth for other clients of the storage system.

A center-wide storage system is shared by various computing resources. For example, the OLCF Spider storage system is shared by production cluster Titan, preparation cluster Eos, analysis cluster Rhea, visualization cluster Everest, various small-scale clusters, an archival system HPSS, and users on login nodes, as illustrated in Fig. 1. The introduction of burst buffers expedites the application write performance. However, draining burst buffers reactively causes I/O contention issues on the underlying storage system, which in return slows down the draining process and accumulates data in burst buffers. More importantly, the I/O contention also impacts the storage system read performance. Computing tasks, such as application restart, analysis tasks, visualization tasks, and user accessing files, are sensitive to read performance degradation.

In order to illustrate such impact, we run an IOR instance with repeating read and write requests to measure the system I/O performance. We run the IOR instance together with the background burst buffer draining requests (i.e., the 12 applications in Fig. 8), and compare the system I/O performance under different burst buffer draining schemes. The read and write throughputs of the IOR instance are shown in Fig. 9. In Fig. 9a, we observe that there are many gaps along the axis of time, where major throughput drops happen. By contrast, read and write throughputs stabilize along the axis of time when applying the proactive burst buffer draining scheme, as shown in Fig. 9b. When I/O provisioning is halved from 4 OSTs to 2 OSTs, the gaps grow much bigger (especially for write requests) when draining burst buffers reactively, as shown in Fig. 9a and Fig. 9c. In contrast, when applying the proactive draining scheme with 2 OSTs, the throughputs of most I/O requests still remain stabilized along the axis of time, as shown in Fig. 9d. According to the comparison, we observe that applying the proactive burst buffer draining scheme preserves the I/O performance for the other clients sharing the storage system, especially when I/O provisioning diminishes.

In order to further analyze the differences between the two draining schemes at block level, we resort to simulation due to the lack of support to collect block level I/O trace on the Spider storage system. We collect application-level I/O traces from the real-system emulations and replay the traces on the Disksim simulator. We utilize the same simulation settings as in Section IV.

The cumulative distribution function of I/O response time is shown in Fig. 10. Concerning system response time, as shown in Fig. 10a, applying the proactive burst buffer draining scheme reduces the system response time significantly. The huge gap between proactive draining and reactive draining is mainly caused by the difference in I/O arrival time. Applying the proactive burst buffer draining scheme delays the arrival time of most of the requests, which leads to a relatively smaller response time. This indicates that applying the proactive burst

![](_page_7_Figure_0.png)

Fig. 9: Available read and write bandwidth of the permanent storage system with the 12 application (in Fig. 8) running at background. Using 4 OSTs, read throughput above 3.2 GB/s and write throughput above 0.9 GB/s are compared. Using 2 OSTs, read throughput above 2.2 GB/s and write throughput above 0.6 GB/s are compared.

![](_page_7_Figure_2.png)

Fig. 10: Cumulative Distribution Function (CDF) of system response time, disk response time, and disk physical access time. System response time is the difference between I/O completion time and I/O arrival time at the disk array level. Disk response time is the aforementioned difference at the disk level. Disk physical access time is the difference between disk response time and queuing time. X-axis is plotted in logarithm scale for better illustration.

buffer draining scheme relieves the burden of the system I/O queue and reduces the system queuing time. For latencysensitive tasks, a shorter queuing time means quicker response. With respect to disk response time, as shown in Fig. 10b, the latency tail is between 1 and 10 seconds using proactive draining and is between 100 and 1000 seconds using reactive draining. Therefore, applying the proactive burst buffer draining scheme reduces the I/O latency tail by orders of magnitude. It should be noted that, the disk response time for many requests are smaller using reactive draining than utilizing proactive draining. This is because the available system I/O bandwidth is much larger between I/O peaks using reactive draining, although the available bandwidth gets much smaller around I/O peaks. In contrast, the available system I/O bandwidth remain relatively steady utilizing proactive burst buffer draining scheme. As a result, compared with proactive draining, many of the I/O requests have a smaller disk response time while a few of them have a much larger disk response time in reactive draining. In order to investigate the cause of the variation in disk response time distribution for both draining schemes, we study the distribution of disk physical access time. As illustrated in Fig. 10c, for most of the I/O requests, the disk physical access time in proactive draining is similar as reactive draining. This indicates that the variation in disk response time is not caused by resource contention. Therefore, the variation is mainly determined by the disk queuing time, which indicates that request contention is the root cause. Comparing with reactive draining, proactive draining scheme reduces system response time significantly and relieves the burden of the system I/O queue. In addition, using proactive draining scheme reduces the variation in disk response time distribution, which preserves the available bandwidth to other clients sharing the storage system.

## *B. Model Validation and Model-driven Study*

In this subsection, first, we validate the accuracy of our I/O provisioning model. Then, we evaluate the I/O provisioning model with leadership applications.

![](_page_8_Figure_3.png)

Fig. 11: Aggregate I/O throughput of conservative model, aggressive model, and simulation.

In the I/O provisioning model, I/O throughput B is derived from simulation results. As long as I/O throughput B is validated, the remaining derivative metrics are valid. We validate the I/O throughput B based on simulation results. The simulation keeps the real system emulation settings with varying numbers of data stripes per sub-request (Nio). Model and simulation results are shown in Fig. 11. Simulation results are denoted as points (crosses), conservative model results are plotted using a blue line, and aggressive model results are depicted as a red line. As illustrated in the figure, the I/O throughput for each draining segment under the same stripe count varies within the vertical range. The aggressive model can accurately capture the average I/O throughput for all the draining segments. Furthermore, the conservative model covers all the I/O throughput data under various stripe counts in a tight manner.

Then, we evaluate the I/O provisioning model with leadership applications as listed in Table III. These are the top 5 largest data-producing applications in the National Center for Computational Sciences at Oak Ridge National Laboratory. We evaluate the case where they run simultaneously on shared storage resources. For simplicity, we assume that

TABLE III: Checkpointing and analysis characteristics of leadership applications [25][26][27]. Checkpointing frequency (freq.) is once per hour for all applications.

| Application | Scientific | Checkpoint | Analysis | Analysis |
| --- | --- | --- | --- | --- |
| Name | Domain | Data Size | Data Size | Dump Freq. |
| CHIMERA | Astrophysics | 160 TB | 160 TB | 1 / hour |
| GTC | Fusion | 20 TB | 10 GB | 1 / minute |
| S3D | Combustion | 5 TB | 5 TB | 1 / 30 minutes |
| GYRO | Fusion | 50 GB | 10 GB | 1 / minute |
| POP | Climate | 26 GB | 1.4 GB | 1 / minute |

![](_page_8_Figure_9.png)

Fig. 12: Overall I/O provisioning requirement of running multiple leadership applications on shared storage resources. Bars denote I/O provisioning requirement for each leadership application using reactive draining. Solid line represents the provisioned bandwidth using proactive burst buffer draining. Dotted line represents the minimum bandwidth in ideal case.

each application runs at the same scale and adopts the Fileper-Process I/O pattern. The I/O provisioning requirement for both checkpoint and analysis for the leadership applications are shown in Fig. 12. Among the leadership applications, CHIMERA has the highest I/O provisioning requirement of 889 GB/s. Exploiting proactive burst buffer draining, ideally, the aggregate draining throughput across all applications can be reduced to 54.5 GB/s. According to the I/O provisioning model, the actual I/O provisioning requirement is reduced to 55.3 GB/s, which is very close to the ideal case as shown in Fig. 12. Therefore, compared with reactive draining, applying the proactive burst buffer draining scheme significantly reduces the I/O provisioning requirement.

#### VI. DISCUSSION

In this section, we discuss the concerns that may compromise the benefits of applying the proactive burst buffer draining scheme from various aspects.

Unknown or Dynamically Changing I/O Periodicity As discussed in Section III, the draining period equals to the timespan of the previous computation segment. The proactive draining controller does not need to know the I/O periodicity of the application in advance. Even if the I/O periodicity changes dynamically due to different failure characteristics [28], [29], [30], [31], the draining period changes accordingly.

Random Write Behavior When applications implement parallel I/O (File-per-Process or Single-shared-file), they may impose random writes on the burst buffer. After all the data is buffered, they are divided into draining segments and are drained to the permanent storage system sequentially.

The Impact of Burst Buffer Draining on Host CPUs Although the proactive burst draining process overlaps with the computation, it is straightforward that I/O operations impose little burden on CPUs. As illustrated in [27], CPU power consumption is extremely low during checkpointing and CPU throttling has little impact on checkpointing performance. Moreover, the proactive draining controller drains smaller groups of data throughout the draining period, which also helps minimize the impact on host CPUs.

Storage Requirement on Burst Buffers The proactive burst buffer draining holds data for an extended timespan. However, it does not impose any higher requirement to the storage capacity of burst buffers, because the draining controller drains all the data before the next data dump. In addition, we assume that node-local burst buffers are provisioned with sufficient capacity to hold the application data. Taking the supercomputer Summit as an example, the 3,400 nodes will be equipped with 800GB of NVRAM each node, which are mainly used as burst buffer or additional node memory [6]. As listed in Table III, the maximum data size of leadership applications is 160 TB, which takes less than 6% of the total burst buffer size.

Support for Failure Restart The proactive draining controller keeps the restart files in the burst buffers until the end of the draining period. Once failures happen, the application can restart from data in node-local storage, for example, using the SCR framework [32]. If the failure cannot be recovered using from node-local storage, it can restart from the permanent storage system. The application can either wait for the checkpoint data to be drained or restart from the latest available checkpoint on the storage system.

# VII. RELATED WORK

I/O bottleneck issues have been studied intensively in HPC systems. Xie et al. [33] characterized the output bottlenecks in supercomputers. In order to improve overall I/O performance, Song et al. [34] and Dorier et al. [35] proposed to reduce I/O interference through cross-application I/O coordination. In order to preserve I/O bandwidth for clients sharing the storage system, researchers proposed various I/O isolation techniques [36] [37] [38]. However, if the I/O performance demand escalates beyond the capability of the storage system, I/O coordination and I/O isolation techniques become less efficient. In this case, Narayanan et al. [39] [40] proposed to offload I/O to idle resources in order to better serve I/O peaks in storage centers.

In order to absorb the bursty bulk data, burst buffers are introduced at different layers of HPC systems. Moody et al. [32] and Bautista-Gomez et al. [41] proposed to use nodelocal storage to buffer HPC checkpointing data. Recently, Oak Ridge National Laboratory announced the introduction of node-local storage in the next-generation supercomputer Summit [6], which serves as burst buffers to absorb the bursty data at node-level. Concerning the off-node aspect, Abbasi et al.[42] proposed scalable data staging services for HPC applications, which allows more efficient data extraction and manipulation. Al-Kiswany et al. [43] proposed to use some of the compute nodes allocated to the application as an intermediate storage system. After that, Costa et al.[44] [45] proposed a predictive method to accelerate the exploration of the optimal provisioning configuration for the intermediate storage system. Besides, Liu et al. [4] first evaluated the design and benefits of burst buffers in HPC systems. Thapaliya et al. [46] proposed to mitigate I/O interference in a shared burst buffer through investigating I/O scheduling techniques. Wang et al. [47] developed a distributed burst buffer file system.

Kougkas et al. [48] proposed a buffer-based I/O coordination strategy to prevent I/O interference on the storage system. The proposed strategy leverages burst buffers to defer conflicting I/O accesses to the storage system. Wang et al. [19] proposed to flush the buffered data in sequential order and coordinate burst buffer draining processes to relieve I/O contention. However, these techniques cannot prevent the burst buffers from passing the I/O peaks on to the underlying storage system. Under this circumstance, reducing the I/O provisioning of the storage system leads to severe I/O contention issues. In this paper, we propose a proactive burst buffer draining scheme to regulate the bursty I/O behaviors and resolve I/O contention issues on the storage system.

#### VIII. CONCLUSION

In this paper we showed that, without judiciously managing the burst buffer draining process, I/O peaks will be passed on to the underlying storage system, causing severe I/O contention. Therefore, we design a proactive burst buffer draining scheme to regulate bursty I/O behaviors and relax the I/O provisioning requirement. Evaluation results show that applying the proactive draining scheme flattens I/O bursts, relieves I/O contention, and preserves the available I/O bandwidth for the other clients sharing the storage system. Then, based on the proactive draining scheme, we develop a model to predict the minimal I/O provisioning requirement. We evaluate the model with leadership applications, and show that the I/O provisioning requirement is reduced to a near minimal level.

#### IX. ACKNOWLEDGMENT

We thank the reviewers for their constructive feedback. We also thank Shayan Moini for helping revise the final version. This research is partially sponsored by Northeastern University and the U.S. National Science Foundation (NSF) under grants CNS-1702474, CNS-1700719, and CCF-1547804. The work was also supported by, and used the resources of, the Oak Ridge Leadership Computing Facility at ORNL, which is managed by UT Battelle, LLC for the U.S. DOE, under the contract No. DE-AC05-00OR22725. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the funding agencies.

### REFERENCES

- [1] Y. Liu, R. Gunasekaran, X. Ma, and S. S. Vazhkudai, "Automatic identification of application i/o signatures from noisy server-side traces," in *Proceedings of the 12th USENIX Conference on File and Storage Technologies*, 2014, pp. 213–228.
- [2] P. Carns, K. Harms, W. Allcock, C. Bacon, S. Lang, R. Latham, and R. Ross, "Storage access characteristics of computational science applications," in *IEEE 27th Symposium on Mass Storage Systems and Technologies (MSST)*, 2011, pp. 1–14.
- [3] P. Carns, K. Harms, W. Allcock, C. Bacon, S. Lang, R. Latham, and R. Ross, "Understanding and Improving Computational Science Storage Access Through Continuous Characterization," *ACM Transactions on Storage (TOS)*, vol. 7, no. 3, pp. 8:1–8:26, 2011.
- [4] N. Liu, J. Cope, P. Carns, C. Carothers, R. Ross, G. Grider, A. Crume, and C. Maltzahn, "On the Role of Burst Buffers in Leadership-Class Storage Systems," in *28th Symposium on Mass Storage Systems and Technologies (MSST)*, 2012, pp. 1–11.
- [5] D. Bard, W. Bhimji, and D. Paul, "Cori phase 1 burst buffer," NERSC Users Group, Tech. Rep., 2016.
- [6] Oak Ridge Leadership Computing Facility, "Summit Fact Sheet," Oak Ridge National Laboratory, Tech. Rep., 2014.
- [7] S. Oral, D. A. Dillow, D. Fuller, J. Hill, D. Leverman, S. S. Vazhkudai, F. Wang, Y. Kim, J. Rogers, J. Simmons, and R. Miller, "OLCF's 1 TB/s, Next-Generation Lustre File System," in *Proceedings of Cray User Group Conference*, 2013, pp. 1–12.
- [8] D. Henseler, B. Landsteiner, D. Petesch, C. Wright, and N. J. Wright, "Architecture and design of cray datawarp," in *Cray Users' Group Technical Conference*, 2016.
- [9] G. Shipman, D. Dillow, S. Oral, and F. Wang, "The Spider Center Wide File System: From Concept to Reality," in *In Proceedings of the Cray User Group*, 2009.
- [10] Oak Ridge Leadership Computing Facility, "OLCF Annual Report," Oak Ridge National Laboratory, Tech. Rep., 2013.
- [11] S. Oral, J. Simmons, J. Hill, D. Leverman, F. Wang, M. Ezell, R. Miller, D. Fuller, R. Gunasekaran, Y. Kim, S. Gupta, D. Tiwari, S. S. Vazhkudai, J. H. Rogers, D. Dillow, G. M. Shipman, and A. S. Bland, "Best practices and lessons learned from deploying and operating large-scale data-centric parallel file systems," in *Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*, 2014.
- [12] R. Miller, J. Hill, D. A. Dillow, R. Gunasekaran, S. Galen, and D. Maxwell, "Monitoring tools for large scale systems," in *In Proceedings of the Cray User Group*, 2010.
- [13] J. Dongarra, "Impact of architecture and technology for extreme scale on software and algorithm design," in *Department of Energy Workshop on Cross-cutting Technologies for Computing at the Exascale*, 2010.
- [14] DOE ASCAC Subcommittee Members, "The Opportunities and Challenges of Exascale Computing," DOE ASCAC Subcommittee, Tech. Rep., 2010.
- [15] R. Stevens and A. White, "A DOE laboratory plan for providing exascale applications and technologies for critical DOE mission needs." in *SciDAC Workshop*, 2010.
- [16] J. Shalf, S. Dosanjh, and J. Morrison, "Exascale Computing Technology Challenges," in *Proceedings of the 9th International Conference on High*
- *Performance Computing for Computational Science*, 2011, pp. 1–25. [17] B. Bland, "Present and Future Leadership Computers at OLCF," in
- *OLCF User Meeting*, 2015. [18] DOE ASCAC Subcommittee Members, "Top ten exascale research challenges," DOE ASCAC Subcommittee, Tech. Rep., 2014.
- [19] T. Wang, S. Oral, M. Pritchard, B. Wang, and W. Yu, "Trio: Burst buffer based i/o orchestration," in *IEEE International Conference on Cluster Computing*, 2015, pp. 194–203.
- [20] J. S. Bucy, J. Schindler, S. W. Schlosser, and G. R. Ganger, *The DiskSim Simulation Environment Version 4.0 Reference Manual*, Carnegie Mellon University, 2008.
- [21] N. Agrawal, V. Prabhakaran, T. Wobber, J. D. Davis, M. Manasse, and R. Panigrahy, "Design tradeoffs for ssd performance," in *USENIX 2008 Annual Technical Conference*, 2008, pp. 57–70.
- [22] E. K. Lee and R. H. Katz, "An Analytic Performance Model of Disk Arrays," in *Proceedings of the 1993 ACM SIGMETRICS Conference on Measurement and Modeling of Computer Systems*, 1993, pp. 98–109.

- [23] P. M. Chen and E. K. Lee, "Striping in a raid level 5 disk array," in *Proceedings of the 1995 ACM SIGMETRICS Joint International Conference on Measurement and Modeling of Computer Systems*, 1995, pp. 136–145.
- [24] H. Shan and J. Shalf, "Using IOR to Analyze the I/O Performance for HPC Platforms," in *In Proceedings of the Cray User Group Conference*, 2007.
- [25] D. Kothe and R. Kendall, "Computational Science Requirements for Leadership Computing," Oak Ridge National Laboratory, Tech. Rep., 2007.
- [26] D. Tiwari, S. Gupta, and S. S. Vazhkudai, "Lazy Checkpointing: Exploiting Temporal Locality in Failures to Mitigate Checkpointing Overheads on Extreme-Scale Systems," in *44th Annual IEEE/IFIP Int'l Conference on Dependable Systems and Networks*, 2014, pp. 25 – 36.
- [27] K. Tang, D. Tiwari, S. Gupta, P. Huang, Q. Lu, C. Engelmann, and X. He, "Power-capping Aware Checkpointing: On the Interplay among Power-capping, Temperature, Reliability, Performance, and Energy," in *46th Annual IEEE/IFIP Int'l Conference on Dependable Systems and Networks*, 2016, pp. 311–322.
- [28] D. Tiwari, S. Gupta, J. Rogers, D. Maxwell, P. Rech, S. Vazhkudai, D. Oliveira, D. Londo, N. DeBardeleben, P. Navaux *et al.*, "Understanding gpu errors on large-scale hpc systems and the implications for system design and operation," in *High Performance Computer Architecture (HPCA), 2015 IEEE 21st International Symposium on*. IEEE, 2015, pp. 331–342.
- [29] S. Gupta, D. Tiwari, C. Jantzi, J. Rogers, and D. Maxwell, "Understanding and exploiting spatial properties of system failures on extreme-scale hpc systems," in *Dependable Systems and Networks (DSN), 2015 45th Annual IEEE/IFIP International Conference on*. IEEE, 2015, pp. 37– 44.
- [30] B. Nie, D. Tiwari, S. Gupta, E. Smirni, and J. H. Rogers, "A large-scale study of soft-errors on gpus in the field," in *High Performance Computer Architecture (HPCA), 2016 IEEE 22nd International Symposium on*, 2016.
- [31] D. Tiwari, S. Gupta, G. Gallarno, J. Rogers, and D. Maxwell, "Reliability lessons learned from gpu experience with the titan supercomputer at oak ridge leadership computing facility," in *Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*. ACM, 2015, p. 38.
- [32] A. Moody, G. Bronevetsky, K. Mohror, and B. R. d. Supinski, "Design, Modeling, and Evaluation of a Scalable Multi-level Checkpointing System," in *Proceedings of the ACM/IEEE International Conference for High Performance Computing, Networking, Storage and Analysis*, 2010, pp. 1–11.
- [33] B. Xie, J. Chase, D. Dillow, O. Drokin, S. Klasky, S. Oral, and N. Podhorszki, "Characterizing output bottlenecks in a supercomputer," in *Proceedings of the International Conference on High Performance Computing, Networking, Storage and Analysis*, 2012, pp. 8:1–8:11.
- [34] H. Song, Y. Yin, X.-H. Sun, R. Thakur, and S. Lang, "Server-side i/o coordination for parallel file systems," in *Proceedings of 2011 International Conference for High Performance Computing, Networking, Storage and Analysis*, 2011, pp. 17:1–17:11.
- [35] M. Dorier, G. Antoniu, R. Ross, D. Kimpe, and S. Ibrahim, "Calciom: Mitigating i/o interference in hpc systems through cross-application coordination," in *Proceedings of the 2014 IEEE 28th International Parallel and Distributed Processing Symposium*, 2014, pp. 155–164.
- [36] M. Wachs, M. Abd-El-Malek, E. Thereska, and G. R. Ganger, "Argon: Performance Insulation for Shared Storage Servers," in *Proceedings of the 5th USENIX Conference on File and Storage Technologies*, 2007.
- [37] A. Gulati, I. Ahmad, and C. A. Waldspurger, "PARDA: Proportional Allocation of Resources for Distributed Storage Access," in *Proccedings of the 7th Conference on File and Storage Technologies*, 2009, pp. 85– 98.
- [38] D. Shue, M. J. Freedman, and A. Shaikh, "Performance Isolation and Fairness for Multi-tenant Cloud Storage," in *Proceedings of the 10th USENIX Conference on Operating Systems Design and Implementation*, 2012.
- [39] D. Narayanan, A. Donnelly, E. Thereska, S. Elnikety, and A. Rowstron, "Everest: Scaling down peak loads through i/o off-loading," in *Proceedings of the 8th USENIX Conference on Operating Systems Design and Implementation*, 2008, pp. 15–28.
- [40] D. Narayanan, A. Donnelly, and A. Rowstron, "Write off-loading: Practical power management for enterprise storage," *ACM Transactions on Storage*, vol. 4, no. 3, pp. 10:1–10:23, 2008.

- [41] L. Bautista-Gomez, S. Tsuboi, D. Komatitsch, F. Cappello, N. Maruyama, and S. Matsuoka, "FTI: high performance fault tolerance interface for hybrid systems," in *Proceedings of 2011 International Conference for High Performance Computing, Networking, Storage and Analysis*, 2011, pp. 32:1–32:12.
- [42] H. Abbasi, M. Wolf, G. Eisenhauer, S. Klasky, K. Schwan, and F. Zheng, "Datastager: Scalable data staging services for petascale applications," in *Proceedings of the 18th ACM International Symposium on High Performance Distributed Computing*, 2009, pp. 39–48.
- [43] S. Al-Kiswany, A. Gharaibeh, and M. Ripeanu, "The Case for a Versatile Storage System," *ACM SIGOPS Operating Systems Review*, vol. 44, no. 1, pp. 10–14, 2010.
- [44] L. B. a. Costa, S. Al-Kiswany, H. Yang, and M. Ripeanu, "Supporting Storage Configuration for I/O Intensive Workflows," in *Proceedings of the 28th ACM International Conference on Supercomputing*, 2014.
- [45] L. B. Costa, S. Al-Kiswany, M. Ripeanu, and H. Yang, "Support for provisioning and configuration decisions for data intensive workflows," *IEEE Transactions on Parallel and Distributed Systems*, vol. 27, no. 9, pp. 2725–2739, 2016.
- [46] S. Thapaliya, P. Bangalore, J. Lofstead, K. Mohror, and A. Moody, "Managing I/O Interference in a Shared Burst Buffer System," in *45th International Conference on Parallel Processing*, 2016.
- [47] T. Wang, K. Mohror, A. Moody, K. Sato, and W. Yu, "An ephemeral burst-buffer file system for scientific applications," in *Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*, 2016, pp. 69:1–69:12.
- [48] A. Kougkas, M. Dorier, R. Latham, R. Ross, and X.-H. Sun, "Leveraging Burst Buffer Coordination to Prevent I/O Interference," in *IEEE 12th International Conference on eScience*, 2016.

