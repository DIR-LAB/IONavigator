# XCollOpts: A Novel Improvement of Network Virtualization in Xen for I/O-Latency Sensitive Applications on Multicores

Lingfang Zeng, *Member, IEEE*, Yang Wang, Dan Feng, *Member, IEEE*, and Kenneth B. Kent, *Senior Member, IEEE*

*Abstract***—It has long been recognized that the Credit scheduler selectively favors CPU-bound applications whereas for I/O-latency sensitive workloads, such as those related to stream-based audio/video services, it only exhibits tolerable, or even worse, unacceptable performance. The reasons behind this phenomenon are the poor understanding (to some degree) of the virtual machine scheduling as well as the network I/O virtualizations. In order to address these problems and make the system more responsive to the I/O-latency sensitive applications, in this paper, we present XCollOpts which performs a collection of novel optimizations to improve the Credit scheduler and the underlying I/O virtualizations in multicore environments, each from two perspectives. To optimize the schedule, in XCollOpts, we first pinpoint the** *Imbalanced Multi-Boosting* **problem among the cores thereby minimizing the system response time by load balancing the BOOST VCPUs. Then, we describe the** *Premature Preemption* **problem and address it by monitoring the received network packets in the driver domain and deliberately preventing it from being prematurely preempted during the packet delivery. However, these optimizations on the scheduling strategies cannot be fully exploited if the performance issues of the underlying supportive communication mechanisms are not considered. To this end, we make two further optimizations for the network I/O virtualizations, namely,** *Multi-Tasklet Pairs* and *Optimized Small Data Packet***. Our empirical studies show that with XCollOpts, we can significantly improve the performance of the latency-sensitive applications at a cost of relatively small system overhead.**

*Index Terms***—Scheduling, hypervisor, multicore, load balancing, I/O virtualization.**

#### I. INTRODUCTION

VIRTUALIZATION as an enabling technology to effectively scale and utilize IT infrastructure has come into the mainstream of enterprise-level computing for business-

Manuscript received November 15, 2014; revised February 15, 2015 and May 3, 2015; accepted May 8, 2015. Date of publication May 12, 2015; date of current version June 12, 2015. This work is supported in part by the National 973 Program of China under grant 2011CB302301, the Fundamental Research Funds for the Central Universities (HUST:2014QN009), Natural Science Foundation of Hubei Province (2013CFB150). The associate editor coordinating the review of this paper and approving it for publication was F. De Turck.

L. Zeng and D. Feng are with Wuhan National Laboratory for Optoelectronics, School of Computer, Huazhong University of Science and Technology, Wuhan 430074, China (e-mail: lfzeng@hust.edu.cn; dfeng@hust.edu.cn).

Y. Wang is with Shenzhen Institute of Advanced Technology, Chinese Academy of Science, Shenzhen 518055, China (e-mail: yang.wang1@siat.ac.cn).

K. B. Kent is with IBM Center for Advanced Studies (CAS Atlantic), University of New Brunswick, Fredericton, NB E3B 5A3, Canada (e-mail: ken@unb.ca).

Digital Object Identifier 10.1109/TNSM.2015.2432066

oriented services. With virtualization, one can easily achieve quick resource re-allocation, ideal fault isolation, and increased flexibility, which are all critical factors to the success of service delivery in terms of performance, security and management. For example, by leveraging the virtual machine (VM) migration technology, a consolidated server can adapt to the dynamic changes of the underlying hardware resources by migrating its hosted VMs to some lightweight machines so as to guarantee the quality of service (QoS). Currently, numerous virtualization technologies in both industry and academia such as VMware [1], Virtual PC [2], and Xen [3] can attain this goal but with different merits and demerits.

Although the benefits of virtualization are appealing, they are not free. The complexity of these virtualized environments not only presents additional management challenges but also impacts the overall performance to applications. One typical example is the I/O-latency sensitive applications, such as those related to stream-based audio/video services. In general, these applications do not require a great amount of CPU time; but they are very sensitive to the network I/O latency. We think this adverse impact could be more or less attributed to two aspects of the current virtualization techniques at both the strategy level and mechanism level. One is the mismatch between the behavior characteristics of the application workloads and the design decisions in the scheduling algorithms (at strategy level). The other is the low efficiency in the underlying network I/O mechanisms to support the small data packet delivery, which is typically commonplace in I/O-latency sensitive tasks (at mechanism level). The observations at these two levels indicate that resource multiplexing, scheduling among virtual machines as well as the design of the virtual network I/O system are still poorly understood, or at least not fully studied in some regards.

In this paper, we study this VM virtual network I/O problem in the context of Xen [3] by optimizing its *Credit scheduler* [4], [5] in conjunction with the underlying supportive network I/O mechanisms. Our goal is to minimize the response time of Xen to the I/O-sensitive applications and while maximize the throughput of the system to these applications as a whole at relative small overhead and impact on the other applications.

Xen as one of the most popular virtualization technologies was renowned for its efficiency and flexibility in resource provisioning and its wide deployments in modern enterprises for business-oriented services. However, its default Credit scheduler and network I/O mechanisms suffer from the same

See http://www.ieee.org/publications_standards/publications/rights/index.html for more information. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

performance flaws or weakness as we discussed in handling the latency-sensitive applications. Therefore, our results would be representative, which are not only beneficial to Xen but also meaningful to a wide range of VM scheduling algorithms to efficiently attack this particular class of applications.

The Credit scheduler [5] was the most frequently used scheduler in Xen, which is characterized by using a credit system to fairly share processor resources while minimizing the wasted CPU cycles in both a *work-conserving* and a *non-workconserving* manner. It has long been recognized that the Credit scheduler algorithm is amenable to computation-intensive tasks where it can achieve high performance by allocating the physical CPU (PCPU) time to virtual CPUs (VCPUs) in a fair and efficient way. However, for I/O-intensive tasks, it could incur a certain degree of latency. In particular, when dealing with I/O data distribution, VCPUs could be frequently switched if there are a large amount of blocked I/O operations, including the control domain (aka *Dom0*) which is subjected to the same scheduling algorithm with other guest VMs. This would adversely impact the overall system performance since Dom0, as the privilege control VM, back-ends the communication directly with I/O devices to complete all the I/O requests made by any other guest VMs (User Domains or *DomUs*).

In addition to the scheduling issues, the performance is further degraded by the underlying virtual network I/O design where a single pair of tasklets for Tx/Rx data transaction in the backend driver (aka netback in Dom0), with all the guest domains (netfronts), could form an I/O throughput bottleneck, especially on multicore platforms. On the other hand, the large number of granted pages required to deliver the small data packets also result in the corresponding amount of hypercalls, a performance overhead for latency sensitive applications.

With these identified performance issues in mind, in this paper we introduce *XCollOpts*, a significant extension of our previous work on the same issue [6]. Compared to the previous work, the optimizations implemented by XCollOpts are holistic since they not only address the identified performance issues in Xen Credit scheduler as detailed in [6] but also optimize the design of Xen I/O virtualization with respect to its communication mechanisms. On one hand, XCollOpts improves the Credit scheduler from two aspects to achieve high performance for the I/O-latency sensitive applications, and on the other hand, it optimizes the virtual network I/O communication mechanisms to accelerate the small network I/O packet transmissions, commonplace in those applications. More specifically, at the strategy level, XCollOpts first minimizes the system response time by balancing the VCPUs with BOOST priority among multiprocessor systems, and then reduces the VCPU dispatching time by monitoring the received network packets and deliberately prevents the scheduler from being prematurely preempted during the packet delivery. Likewise, at the mechanism level, XCollOpts deploys multiple Tx/Rx tasklet pairs instead of the single pair in the backend driver domain to fully utilize the multicore resources while minimize the number of granted pages for efficient delivery of the smallsized packets. Our empirical studies show that the proposed XCollOpts optimization can significantly improve the performance of Xen virtual network I/O performance while keeping the system overhead to a minimum. These results are not only beneficial to the I/O-sensitive application segments but are also relevant to network and service management where "carriergrade" solutions are being sought with the virtualization of network functions. For example, ClickOS [7], a Xen-based software platform, was most recently proposed to optimize middlebox processing with respect to network-latency reduction and throughput improvements. Our techniques are also useful in this respect to improve NFV-based network equipment, such as virtual routers for virtual network migration to adapt to the dynamic changes of physical substrate resources [8].

The remainder of the paper is organized as follows. We conduct a system overview on Xen virtualization as the background knowledge in Section II we analyze some potential performance issues of Xen to latency sensitive tasks in Section III. With these issues in mind, we introduce the XCollOpts optimizations on the Credit scheduler and the network I/O virtualizations in Section IV and Section V respectively. The performance evaluation on the proposed optimizations is presented in Section VI, and some related work is overviewed in Section VII. Finally, we conclude the paper with some directions for further work in Section VIII.

#### II. SYSTEM OVERVIEW

Xen virtualization is a layer of software, termed a *Virtual Machine Monitor* (VMM) or *hypervisor* in Xen parlance, which abstracts the underlying hardware resources of a single physical server into multiple instances of virtual machines (VMs) (aka *Domains* in Xen), co-existing and co-executing simultaneously. The VM presents the virtualized resources such as CPUs, physical memory, network connections, and block devices as an illusion of a real machine to the overlying guest OSes and applications. The virtualized resources for each domain are enforced and managed by the hypervisor which includes the VCPU scheduling algorithms, defaulted by the Credit scheduler, and the underlying inter-domain I/O communication mechanism as the key components to the efficiency of the virtualization.

#### *A. Xen's Credit Scheduler*

The Credit scheduler is a fair share algorithm based on the proportional scheduling. According to its weight, each domain is assigned a certain *credit* value, representing the CPU share it is expected to have. Therefore, if each domain is given the same number of credits, the domains should have an equal fraction of processor resources. The credits of the running domains, as the cost paid for the processor resources, are deducted periodically (100 credits for every 10 ms via scheduler interrupts, but a domain that runs for less than 10 ms will not have any credits debited). Whenever its credit value is negative, the domain is in OVER priority (i.e., OVER VCPU) otherwise, in UNDER priority (i.e, UNDER VCPU). Every so often (30 ms), a systemwide accounting thread recomputes the credits earned by each running domain according to its weight.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

By default, Xen allocates only one VCPU to each domain when the domain is created,1 and it contains general information related to scheduling and event channels (discussed later). To support the numerous processes in the guest OSes and applications, VCPUs will be scheduled among the PCPUs, which is achieved by maintaining a local ready VCPU (domain) queue (aka run queue) for each PCPU. The queue is periodically sorted in such a way that UNDER VCPUs will always run ahead of OVER VCPUs, and the ordering within each priority is round-robin. The system always schedules the VCPU to run that is at the head of the queue. The selected VCPU will receive 30 ms before being preempted to run another VCPU. OVER VCPUs cannot be scheduled unless there are no UNDER VCPUs in the run queue, implying that a domain cannot use more than its fair share of the processor resources unless the processor(s) would otherwise have been idle. When a processor is idle or the processor's run queue has no more UNDER VCPUs, it would check other processors to find any eligible VCPUs to run on this processor, achieving the global load balancing.

However, due to the lack of notion of urgency, the original Credit algorithm is merely amenable to the compute-intensive workloads and biased against the I/O-latency sensitive applications. To address this problem and minimize the latency of I/O event handling, a boost mechanism is introduced into the Credit scheduler by adding a new priority BOOST to the system so that a VCPU with BOOST priority (i.e., BOOST VCPU) is allowed to preempt a running UNDER VCPU. The current Credit scheduler boosts the priority of the blocked VCPU in UNDER to BOOST after it is woken by receiving an event over the event channel. The woken VCPU preempts the running VCPU at once rather than entering the run queue to compete with other domains. As a consequence, the response time of the I/O sensitive tasks is reduced.

#### *B. Inter-Domain Communications*

According to Xen, domains in the same physical machine are not in the same functional class. Dom0 as a privileged domain (i.e., control domain) is created during the boot time to take responsibility for hosting the application-level management software, including the control of other domains, termed DomUs in Xen (e.g., domain creation, domain termination). In particular, Dom0 can function as a driver domain if it hosts the device drivers and performs I/O operations on behalf of the DomUs.2 In contrast, DomUs are unprivileged guest domains, which present the virtualized resources to the overlying guest OSes and applications. They cannot directly access the physical hardware on the machine. Rather, to accomplish an I/O operation (i.e., network and disk accesses), DomUs have to cooperate with Dom0 by using two ring buffers: one for packet transmission and the other for packet reception. The ring buffers are implemented in Xen based on *grant tables* and *event channels*. The grant tables are a mechanism to share (page sharing) or transfer (page flipping) memory pages between domains. By using grant tables one domain can notify the hypervisor to grant another domain access to its own memory pages, including writing, reading or exchanging, depending on the grant rights. The hypervisor keeps the grants in a *grant reference table* and passes the grant reference onto the other domain and signals this I/O request via the event channels (by using *hypercall* to pend a virtual interrupt in the event channel of the target domain). The target domain will check its event channels when it is scheduled and deliver the pending event by invoking the corresponding interrupt handler (e.g., forwarding the requests to the native device driver in Dom0). Clearly, the latency between pending and delivering the event depends on the underlying VM scheduling algorithms.

#### III. PERFORMANCE ISSUE ANALYSIS

In this section we analyze some performance issues in the current Xen virtual network I/O systems, which motivated our research. The rationale of discussing the Credit scheduler in this context is the high coupling of the scheduling strategies and the underlying virtual network system in terms of the performance optimization.

#### *A. Issues in Xen Credit Scheduler*

Improving the Credit scheduler to assure that I/O domains will get timely response has long been an active research topic. Although various methods have been proposed [9]–[14], in practice I/O latency is still an obstacle, leaving much room unexplored for further improvements. In this section, we identify some not fully-studied sources of performance flaws in the current Credit scheduler on multicore platforms that could slowdown the I/O-sensitive applications. We refer to them as *Imbalanced Multi-Boosting* and *Premature Preemption*.

*1) Imbalanced Multi-Boosting (IMB):* Multi-Boosting (MB) refers to the phenomenon that multiple domains could be boosted at the same time. This phenomenon can be often observed in I/O-intensive applications due to Xen's split driver model as we discussed. For example, consider a scenario in which two packets destined to two different blocked UNDER domains arrive consecutively. If the driver domain is UNDER, then after forwarding the first packet, it will be preempted by the target domain which is just boosted. During the processing of this boosted guest, the second packet arrives, the driver domain is woken up and also boosted. Then the hypervisor tickles the scheduler to select the driver domain to run again with BOOST priority (the first BOOST domain is preempted), which sends a virtual interrupt to the second target domain via the event channel. The second UNDER domain will enter the BOOST state whenever it receives the event. So at that time, all three domains are temporarily in BOOST priority, and two of them have to wait in the queue for execution. Generally, if the driver domain has multiple packets that are destined to multiple

<sup>1</sup>Xen also allows a domain to have access to more than one CPU by allocating more than one VCPU. For easy presentation, we assume that each domain is configured by one VCPU. Thus VCPU and domain can be interchangeable in the discussion.

<sup>2</sup>Current Xen-based systems usually employ the *Isolated Driver Domain* (IDD) to conduct real I/O operations to improve the reliability and safety of the system.

![](_page_3_Figure_1.png)

Fig. 1. Distribution of the BOOST VCPUs among the physical CPUs. 32 guest domains are evenly divided into 4 groups, each having 8 domains concurrently running on Xen-3.4.2. Xentrace is used to create a record whenever a VCPU enters BOOST state in a time interval of 1s. (a) zip. (b) ping.

user domains, then all the designated user domains are boosted, which clearly negates the value of the BOOST state.

MB was first identified by Ongaro *et al.* [10] in their original paper of introducing BOOST, and later studied in [15] for realtime Credit scheduling. In this paper, we study this problem in the context of multicores and identify the *Imbalanced Multi-Boosting* problem, which is distinct from the previous studies.

Although the Credit scheduler is recognized for its global load balancing, it does not distinguish the states of the VCPUs to balance the loads among PCPUs. As a consequence, it could happen that for some PCPUs, there are more BOOST VCPUs waiting in the queue to be scheduled, while for others, there are fewer or even no BOOST VCPUs in the queue. We thus call this phenomenon Imbalanced Multi-Boosting (IMB).

We can observe IMB from Fig. 1 which shows the uneven distribution of the BOOST VCPUs for two I/O intensive benchmarks on a quad-core platform with 32 test domains (excluding Dom0) concurrently running on Xen-3.4.2, each being allocated one VCPU and running CentOS 5.2. Dom0 was used as the driver domain and the guest domains were evenly divided into four groups, each with eight domains. Each domain in the first group ran *zip&gzip* tools to compress the source files of Linux-2.6.18 while each domain in the second group responded to a sequence of remote *ping* requests over a Gigabit Ethernet. In both cases, the distribution of BOOST VCPUs are not well balanced between the cores, so some BOOST VCPUs are processed much slower than the others. Therefore, IMB is an important problem to the I/O-sensitive tasks.

*2) Premature Preemption (PP):* According to Xen's I/O model, arriving packets are first delivered to the hypervisor where the associated physical interrupts are virtualized and sent to the driver domain via the event channel. The driver domain demultiplexes the packets after it receives the corresponding virtual interrupt, and then notifies the availability of one or more packets to a target guest domain (also via the event channel connected with the guest) which will be woken up by the hypervisor if it is blocked on those packets. Since sending an event will result in the scheduler tickle, the PP problem will be caused as the driver domain could be preempted by a BOOST guest domain even though it has multiple pending interrupts for the arriving packets not being processed. In this situation, the driver domain is prematurely scheduled out, in the sense that some guest domains cannot timely receive their notices and have to wait until the driver domain is re-scheduled by the hypervisor, rendering the whole system to be less responsive.

The PP problem was also first discussed in Ongaro *et al.* [10] but has not been well studied since then. To avoid preempting the driver domain, Ongaro *et al.* suggested disabling the scheduler tickles but they did not evaluate the impact. Later, Yoo *et al.* [15] mitigated this problem on Xen-ARM from a realtime prospective by proposing a similar strategy that does not allow the driver domain to be scheduled out when it disables the virtual interrupts instead of the physical interrupts. In this paper, we study this problem on multicore platforms, which can be viewed as an extension or complement to the existing work.

#### *B. Issues in Xen I/O Virtualization*

Optimizations on the Credit scheduler could not be fully exerted if the performance issues of the underlying supportive communication mechanisms are not considered. Therefore, in addition to the Credit scheduler, we also delved into the I/O virtualization in Xen and identified two design flaws, which could result in performance issues for I/O-sensitive workloads. We call the first flaw *Single Tasklet Pair* (STP) and the second *Small Data Packet* (SDP).

*1) Single Tasklet Pair (STP):* Given the background knowledge of the inter-domain communication, we can easily identify the data transmission and reception mechanism in Xen, which is implemented as a single tasklet pair for Tx/Rx data transactions between the backend driver in Dom0 and the front-end driver in a DomU that intends to have an I/O request. Such a netback tasklet pair could only run at one VCPU at a time, and it is used to serve all the netfronts. Therefore, only the VCPU which handles the tasklet will become overloaded, leading to a performance bottleneck.

An illustrative architecture is shown in Fig. 2(a) where each time a DomU has an I/O communication resorting to Dom0, this tasklet pair will be established, and maintained until the communication finishes. This single tasklet pair is shared among all the communicating guest domains; such a use pattern limits the system throughput, especially on the multicore platforms. As such, distributing the netback's I/O workloads to different tasklets, each being bound with different VCPUS in Dom0 either by irqbalance or manual pin interrupt, would on average deliver the total CPU utilization to each VCPU so that the scalability of the Dom0 is improved to facilitate the I/Osensitive applications.

*2) Small Data Packet (SDP):* With the grant table mechanism in Xen, one domain can notify the hypervisor to grant another domain access to its own memory pages (i.e., delivery pages). As a result, in order to send a packet, the hypervisor needs to switch from the guest to the hypervisor, which is done with the lockless ring data structures as shown in Section II-B. Although these data structures are efficient to minimize the overhead of context switching for batch requests, they do not work well for I/O-sensitive applications with respect to the transmission/reception of small data packets. This is because for each small data packet communication, a hypercall to the grant page has to be made, which would result in a large number of highly expensive context switches, degrading the Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

![](_page_4_Figure_1.png)

Fig. 2. Diagram of data packet processing in the backend domain. (a) Single tasklet pair. (b) Small data packet.

overall network performance. The root cause of this overhead is that the granularity of the exchanged data packet is not considered in the design. Fig. 2(b) shows a simplified data transmission procedure that grants a page to send a small data packet with less than 4 KB. Clearly, if the number of small data packets is very large, the incurred overhead due to the granting hypercalls cannot be neglected as it not only slows down the the data packet transmission/reception speeds but also degrades the overall network throughput. Therefore, addressing this problem could substantially improve the performance of I/O-sensitive applications as the data packets of those applications are usually small.

# IV. OPTIMIZED CREDIT SCHEDULER

Given the description of the identified performance flaws in the Credit scheduler for the I/O-sensitive applications, in this section we present its XCollOpts optimization on these issues, which includes the load balancing algorithm for the BOOST domains and the algorithm for preventing of the premature preemption in the network packet dispatching.

## *A. Load Balancing of BOOST Domains (LB)*

As we showed in the last section, the current scheduler could cause the IMB problem, which potentially leads to the uneven distribution of BOOST domains among the PCPUs. Although the Credit scheduler can achieve global load balancing, it has little effect on the balance of the BOOST domains, making the system less responsive as a whole. To address this problem, in XCollOpts we re-organize the run queue in XCollOpts into a priority queue (using red-black tree) instead of periodically sorting it in every 30 ms. Then we perform a load balance for the BOOST VCPUs across all PCPUs in order to improve the response time of VCPU. Our load balancing algorithm is shown as follows,

After a BOOST domain is woken up and inserted into a run queue, the hypervisor will tickle the scheduler to make a scheduling for the PCPU associated with that queue. However, before this action is performed, we first run a simple load bal-Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

ancing algorithm, which performs in O(log n) time complexity where n is the maximal run-queue length,

- 1) Checks whether the current running VCPU on the corresponding PCPU is BOOST or not?
- 2) If yes, selects the target PCPU based on some criteria VCPUs to migrate (discuss below). However, if the selected target and source PCPU are the same, then exits. Otherwise, inserts the VCPU into the run queue of the target PCPU.
- 3) Otherwise, if the current running VCPU is not BOOST, triggers the PCPU scheduling as usual, and then exits.

In a multicore system, the target PCPU is selected according to the following criteria (ties are broken arbitrarily),

- 1) Searches the free PCPU in accordance with the order of the same core, the same socket, different sockets. If found, then returns the PCPU number.
- 2) Searches the PCPU not running a BOOST VCPU in accordance with the order of the same core, the same socket, different sockets. If found, then returns the PCPU number.
- 3) Finds the PCPU whose run queue includes the least BOOST VCPUs, then returns the PCPU number.

The rationale behind these criteria is the spatial locality of the computations. For example, if two PCPU share the same core, they can also share the same local cache. Clearly, the search is linear in the number of the PCPUs, and thus very efficient.

# *B. Prevention of Premature Preemption (P3)*

This section introduces the optimization algorithm in XCollOpts to prevent the driver domain from being prematurely scheduled out (i.e., the PP problem). The basic idea of this algorithm is when there are multiple pending packets for dispatching, the driver domain will inform the underlying hypervisor of this fact, which as a response will not tickle the scheduler until the driver domain dispatches all these packets and yields.

*1) Dispatching Vector:* The core data structure of this algorithm is a *dispatching vector* of size equal to the number of PCPUs in the platform. The vector is created in the hypervisor at boot time and then shared with the driver domain. Each bit represents a PCPU, and the bit value is set by the driver domain and used by the hypervisor. The value of 1 indicates the corresponding PCPU is dispatching packets while the value of 0 denotes that the PCPU is not doing such work.

*2) Prevention Algorithm:* The algorithm runs inside the driver domain whenever a packet is arriving or has been dispatched to the target guest,

- 1) Depending on whether or not the number of I/O virtual interrupts in the event channel is greater than one, the algorithm notifies the hypervisor by setting or clearing the corresponding bit in the vector via a hypercall.
- 2) When the scheduler is tickled by the hypervisor, it first examines the value of the bit that corresponds to the PCPU running the domain driver.
- 3) If the value has been set to one, then scheduling on the corresponding PCPU is disabled, which means the driver domain cannot be preempted while dispatching packets. Otherwise, scheduling is performed as usual and the driver domain could be preempted.

Our algorithm is simple yet efficient to achieving the goal in constant time as only one bit vector is shared between the driver domain and the hypervisor, and the shared bit vector is only updated by the domain driver, incurring no synchronization cost.

# *C. Algorithm Combinations*

The two proposed algorithms in XCollOpts are independent of each other. They are designed for different problems and invoked at different time during the execution. Currently, the LB algorithm for load balancing the BOOST VCPUs is invoked by the hypervisor after a BOOST VCPU is inserted into a queue and before the scheduler is tickled. This is reasonable under the assumption that each BOOST VCPU has an equal opportunity to preempt the running VCPU, implying that the driver domain can be scheduled out at any time. However, this assumption is not always true when considering the effects of the prevention algorithm (P3) since the driver domain cannot be preempted arbitrarily. In this situation, the prevention algorithm should be designed in conjunction with the load balancing algorithm for further performance improvements. More specifically, according to the original scheduler, after a VCPU is boosted, it likely preempts the running driver domain even though it has pending packets. However, in our implementation, this premature preemption is temporarily forbidden, and a new PCPU has to be selected for this new woken-up BOOST VCPU with the stated load balancing in mind. Therefore, with XCollOpts, the performance can be improved with the reduced response time.

#### *D. Remarks*

The MB problem has long been recognized. However, the imbalanced BOOST VCPUs caused by this problem on multiprocessor platforms has not yet aroused much attention in the literature. To our best knowledge, we are the first to investigate Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

this special load balancing problem. Although our method is simple, it is effective to improve the latency-sensitive applications, which will be evidenced by the empirical studies in the next section. There is still some room for further improvements. For example, we did not consider the temporal locality and queue features other than the number of BOOST VCPUs in the current PCPU selection criteria.

The idea of disabling scheduler tickle to prevent the PP problem was first advocated by Ongaro *et al.* in [10] but left unexplored. Our method can be viewed as an extension of their idea to the multiprocessor platforms. The subtle, but rather important extension is that we allow the scheduler to be tickled, but forbid scheduling the PCPU on which the driver domain is running.

Like the proposed load balancing algorithm, there are also several points in the prevention algorithm which can be further improved. First, we can use a *counter* vector instead of a bit vector to track the number of pending packets in the driver domain. The advantage of using a counter vector is that the value of the corresponding counter can be increased or decreased on the fly with respect to the packets arriving at or leaving from the driver domain, saving work each time in checking the event channel. However, an issue with this improvement is the size of the counter, the *probabilistic counting* could be a potential solution to this issue for further study.

Second, as a side effect, the prevention algorithm could pin down the driver domain to the PCPU if it has a large number of pending packets, we therefore need new optimizations on both the scheduling algorithms and the network I/O mechanisms running in due course to address this problem; the current time slice of 30 ms may not suffice, but a large time slice (>30 ms) may also have negative effects on the fairness of the Credit algorithm, especially for compute-intensive applications on single-processor platforms.

#### V. OPTIMIZED I/O VIRTUALIZATIONS

Following the improvements of the Credit scheduler, in this section we present the XCollOpts optimizations on the network I/O virtualizations in Xen to address the identified issues in supporting I/O-latency sensitive applications.

#### *A. Multiple Tasklet Pairs (MTPs)*

The basic idea of this optimization is instead of sharing a single tasklet for guest domain communications, XCollOpts uses multiple tasklet pairs to load balance the communication tasks. It implements this optimized mechanism by pre-registering a number of tasklet pairs in the backend driver through its initialization functions, each corresponding to net_rx_action() and net_tx_action(), which are the designated functions in charge of sending and receiving data packets in Xen network I/O virtualizations. In general, the number of pre-registered tasklet pairs can be any value, but typically it is equal to the number of the allocated VCPUs to the current Dom0. The architecture of the virtual network I/O after optimized is shown in Fig. 3(a). Comparing with Fig. 2(a), we can easily observe that the new mechanism relies on multiple tasklet pairs to balance

![](_page_6_Figure_2.png)

Fig. 3. Diagram of the optimized data packet processing in the backend domain. (a) Multiple tasklet pairs. (b) Optimized small data packet.

the data communications across all the domains, breaking the performance bottleneck, especially on the multicore platforms where the multiple tasklet pairs can work in parallel. Our empirical studies show that this optimization not only accelerates the data communication speed of each domain, but also improves the overall system throughput.

*B. Optimization for Small Data Packets*

Similar to the first optimization, the essence of this optimization to the second performance issue in the I/O virtualization is also easy to understand. Instead minimizing the overhead along the critical path to grant pages, XCollOpts tries to reduce the number of grant pages so that the total number of hypercalls involved can be reduced correspondingly. To this end, XCollOpts re-designs the data communication mechanism, in particular for small data packets. In this section, we focus squarely on its data transmission part. As for the data reception, the procedure is largely the same as its transmission counterpart.

*1) DomU to Dom0:* As we shown in Fig. 3, each *socket buffer*, or skb,3 even with small size, would require a grant page for the delivery. Therefore, when there is a large amount of small packets, each carrying out a small-size payload, we can observe a large number of grant pages, resulting in a high performance overhead. To reduce this overhead, XCollOpts tries to minimize the grant operations by moving the memcpy operation to the front-end domain as shown in Fig. 3(b). To this end, XCollOpts pre-allocates 256 pages, manages them at the backend domain (Dom0), and grants it once as a memory pool to the front-end domain (DomU) where the memcpy is performed without the overhead of grant operations.

*2) Dom0 to DomU:* The optimization on the opposite data reception is similar to the transmission. The difference is that the memory pool is allocated at the front-end domain and grants it once to the backend domain, and in the meantime, the memcpy is moved to the backend domain accordingly to reduce the number of grant pages.

By combing these optimizations, XCollOpts can accelerate the process in transmitting and receiving the small data packets and as a result, minimize the response time and improve the network I/O throughput for the latency-sensitive applications.

#### VI. PERFORMANCE EVALUATIONS

In this section, we perform empirical studies on the proposed XCollOpts optimization. After introducing the experimental setup, we first evaluate its scheduling algorithms by measuring the response times of a latency-sensitive application, and then assess its optimization on the performance of the network I/O virtualizations. Finally, we measure its system overheads to evaluate its benefits in reality. Our numerical results show that with marginal system overheads, XCollOpts can not only reduce the response time of latency-sensitive tasks, but also improve the overall system performance on processing small data packets, which is also critical to the latency-sensitive applications.

## *A. Experimental Setup*

Our experimental setup to evaluate the improved scheduler includes two physical machines and 32 virtual machines (excluding the driver domain). The two physical machines are connected by a Gigabit Ethernet and each of them is configured according to Table I. All the virtual machines are installed on one physical machine and managed by Xen-3.4.2 while the other one as a remote machine communicates with those virtual machines.

We configure each domain based on Table II and use CentOS 5.2 as the guest OSes in the driver domain (i.e., Dom0 in our experiments). Recalling that the major goal of this research is to optimize the latency-sensitive applications by reducing the response time, we deliberately select the ping program as our benchmark since this program is usually adopted for this purpose in the literature [10], [14]. Concretely, a remote system

<sup>3</sup>The socket buffer is the most fundamental data structure in the Linux networking code, which is used to handle every packet sent or received in the system.

TABLE I HARDWARE CONFIGURATION

| CPU | Intel Xeon E5462 2.80GHz |
| --- | --- |
| RAM | 16GB RAM |
| Core | Yorkfield (45 nm) / Stepping: C0 |
|  | number of cores: 4 |
| Logic processor | 4 |
| Socket | Socket 771 (FC-LGA6) |
| frequency | 2.80 GHz (400 MHz ×7.0) |
|  | FSB: 1600 MHz |
| L1 data cache | 4 × 32 KB, 8-Way, 64 byte lines |
| L1 code cache | 4 × 32 KB, 8-Way, 64 byte lines |
| L2 cache | 2 × 6 MB, 24-Way, 64 byte lines |
|  | rate: 2800 MHz |
| HardDisk | 320G IDE |
| NIC | 1Gbps |

TABLE II DOMAIN (VM) CONFIGURATION

| Kernel | "/boot/vmlinuz-2.6.18.8-xen" |
| --- | --- |
| Ramdisk | "/boot/initrd-2.6.18.8-xen.img" |
| Memory | 256 |
| Name | "DomU" |
| VCPUs | 2 |
| Disk | ['file:/dom1.img, hda1, w'] |
| Root | "/dev/hda1 ro" |

is used to send pings to the guests who only acknowledge the receipt of the ping packets without doing any other computations. We use this benchmark to measure the network latency to evaluate the XCollOpts optimization algorithms.

To measure the improved network throughput, we still set up the experiments based on the existing configurations but upgraded the connection between the two physical machines with a Gigabit Ethernet rather than the 100 Mbps Ethernet used in the previous configuration since high-speed networks are much more popular today, and on the other hand, in reality the most stringent delay requirements of some latency sensitive traffic such as voice are always met by provisioning the network with enough bandwidth [16]. Therefore, in these experiments, we focus on XCollOpts optimization on the Gigabit Ethernets.

# *B. Response Time Minimization*

In the following set of experiments, we focus on the XCollOpts optimization on the Credit scheduler to minimize the response time of the latency-sensitive applications. We first evaluate the load-balancing algorithm followed by assessing the algorithm for preventing the premature preemption.

*1) Load-Balancing of BOOST Domains:* To evaluate the LB optimization on the BOOST domains, we first create 20 guest domains, which are evenly divided into two groups, each with 10 virtual machines, and allow each machine in the second group to ping a machine in the first group every second so that a large amount of BOOST VCPUs would be generated. We then measure each ping response time. The comparison results before and after the improvements are shown in Fig. 4 where we can find that the packet response time is not only dramatically reduced after the optimization but also relatively stable between each ping operation, demonstrating the benefits of the load balancing among the BOOST domains.

![](_page_7_Figure_10.png)

Fig. 4. The runtime of ping program before-LB optimization and after-LB optimization.

TABLE III COMPARISON OF THE LOAD BALANCE FACTORS OF FIG. 1 AND FIG. 6

| | Group | w/o Opt. | w Opt. |
| --- | --- | --- |
| | (a) zip (Linux-2.6.18) | 0.67 |  | 0.86 |
| (b) ping (1 GigE) | | 0.51 | 0.83 |

This phenomenon is not difficult to understand as during the scheduling, the BOOST VCPUs are organized to wait in the run queue, which would cause the VCPUs in the front of the queue to have more opportunities to get scheduled quickly and thus shorten the ping response time; but for the VCPUs in the rear of the queue, they would be scheduled slowly, lengthening the ping response time and resulting in its unstableness (see Fig. 1). In contrast, after improvements with load balancing, BOOST VCPUs are distributed evenly into each physical CPU's run queue so that on average the number of BOOST VCPUs in each run queue is decreased accordingly. We can validate this by comparing the load balance factor β of Fig. 1 and Fig. 6 which are obtained under the same configurations with and without the optimization. The load balance factor β is defined as:

$$\beta=\frac{\mbox{ave}\{n_{i}:0\leq i<p\}}{\mbox{max}\{n_{i}:0\leq i<p\}}\tag{1}$$

where ni : 0 ≤ i < p is the number of BOOST VPCUs in the run queue associated with PCPUi and p is the total number of the PCPUs. Clearly, β ≤ 1 and the larger, the more balanced.

By computing the load balance factors of both figures in Table III, we can see that XCollOpts balances the BOOST VCPUs among the cores. Furthermore, with XCollOpts, even a BOOST VCPU at the backend of the run queue would not be waiting too long for the scheduling, which consequently reduces the (average) number of BOOST VCPUs associated with times each PCPU. Therefore, the ping response time fluctuates slightly, approximately around 0.08 ms, which is relatively stable compared with prior to improvement.

*2) Prevention of the Premature Preemption:* As the system performance will be degraded if the back-end driver is frequently switched off in the process of dispatching network packets, the number of domains involved in this experiment should be increased accordingly so that the advantages of this

![](_page_8_Figure_1.png)

Fig. 5. The ping time distribution before-P3 optimization and after-P3 optimization.

![](_page_8_Figure_3.png)

Fig. 6. Distribution of the BOOST VCPUs among the physical CPUs under the same configurations with Fig. 1 after the optimization. (a) zip. (b) ping.

optimization would be prominently displayed. To this end, we still create 20 virtual machines and another machine to ping these 20 virtual machines. In this way, a large number of the ping packets have to be dispatched by the backend dispatcher to multiple blocked VCPUs. We measure the distribution of the response time of the first 1000 ping requests as the metric to evaluate the optimization. Fig. 5 shows the comparison results on the distribution before and after the improvements. From this figure, we can clearly see that a large percentage of the response time before the improvement falls into the interval greater than 0.10 ms whereas for the improved results, it is less than 0.10 ms, demonstrating the effectiveness of our optimization to the latency-sensitive applications.

The results are straightforward. Before the optimization, due to the extensive communications between the number of guest domains, it is highly likely that the VCPUs allocated to the back-end driver domain would be preempted by the VCPUs just woken-up in other domains. As a consequence, it would delay to wake up some other VCPUs to dispatch the ping packets. This is evidenced by the hash bars in Fig. 5 where the ping response time greater than 0.1 ms occupies a large percentage (close to 47%) of the total results. With the P3 optimization, the VCPUs in the back-end driver domain are prevented from being switched off during the packet dispatching. As a result, the ping response time after improvement is less than 0.1 ms in a large part (about 75%) as shown by the dotted bars in Fig. 5.

# *C. Improved Network Throughput*

To evaluate the optimizations on the network throughput, we first install Dom0 on one machine and then create eight guest domains, each being equipped with the netperf tool to measure the network performance [17]. In the meantime, we also install the tool on the other ancillary machine from which we use the tool's command line to monitor the eight guest domains and measure their throughput performance. In the experiments, we first evaluate the effects of the multiple tasklet pairs and then assess the optimization on SDP in the network virtualizations. Since the different runs of our experiments are relatively stable, the standard deviations of the experimental data sets are very small, and thus, not shown in the figures.

*1) Multiple Tasklet Pair Optimization:* Fig. 7(a) shows how MTP optimization improves the network throughput over a the original unoptimized one. From this figure, one can easily find that the optimized throughput a has a remarkable improvement. By a simple calculation, the overall throughput increases from 2689 Mb/s to 3005 Mb/s, a approximately 11.75% improvements. These results are also consistent with our initial expectation as with changing a from STP to MTP, Dom0 can fully utilize its multiple allocated VCPUs, which amounts to the exploitation a of the multicores (or SMPs) to attain performance benefits via parallel processing.

*2) Optimization on Small Data Packets:* To evaluate the optimization on SDP, we deliberately vary the packet size from 2 KB to 8 KB with focus squarely on the throughput changes. Fig. 7(b)–(d) compare the optimized throughput with the one before being optimized given the different packet sizes 2 KB, 4 KB and 8 KB. From Fig. 7(b), we can see that when the packet size is small, the optimization allows Xen over the Gigabit Ethernets to have a remarkable improvement to its I/O throughput, which is approximately 13.03%. This performance improvement remains largely unchanged until the packet size reaches up to 4 KB (13%) as shown in Fig. 7(c). However, when the packet size continues to increase to 8 KB, Fig. 7(d) indicates that the performance benefits of the optimization are diminished. As a result, the optimized throughput and the unoptimized throughput are largely the same. The reason is that we only modified the data communication procedure for the small packet size (≤ 4 KB), whereas for the large packet size (> 4 KB), the data communication mechanism is not touched (Table IV).

From these experiments, we can see the effectiveness of the optimization in XCollOpts on the small data packet communications. By pre-allocating a memory pool and granting its access to the other end-domains at once while moving the memcpy operation oppositely, Xen can minimize the number of grant pages so as to accelerate the processing of the small data packets, and thus improve the overall throughput over the Gigabit Ethernets, which is critical to I/O-latency sensitive applications.

# *D. Impact on Other Workloads*

In addition to the microbenchmarks, the following set of experiments are conducted to evaluate the effects of the proposed algorithms on other workloads. Since the Credit scheduler Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

![](_page_9_Figure_1.png)

Fig. 7. Throughput comparisons before and after the optimization on MTP and SDP. (a) MTP Opt.; (b) 2 KB data packet. (c) 4 KB data packet. (d) 8 KB data packet.

TABLE IV COMPARED TURNAROUND TIMES FOR THE SYSBENCH PRIME-SUM BENCHMARK BEFORE-IMPROVED AND AFTER-IMPROVED. THE DEFAULT VCPU QUEUE LENGTH IS 4

| #VCPU |
| --- |
| Before-improved (s) || 361.823 | 724.438 | 1086.978 | 1452.598 | 1807.154 | 2215.224 | 2533.542 | 2895.687 |
| After-improved (s) || 361.758 | 722.989 | 1084.652 | 1447.488 | 1807.065 | 2215.439 | 2533.453 | 2895.406 |

attempts to fairly share the processor resources, we will show how the proposed algorithms impose a small impact on the compute-intensive benchmark and some positive impact on the disk I/O-intensive benchmark as well in terms of fairness.

Fig. 9(a) shows the CPU utilization that is allocated among seven concurrent domains with equal credit allocations. The experiment simply allows each domain to execute a macrobenchmark, *lookbusy*, which is a simple application for generating synthetic workloads on Linux systems [18]. As the figure shows, the enhanced Credit scheduler successfully achieves the CPU fairness, implying that the impact of our proposed algorithms is small. This observation is not difficult to understand as CPU-intensive VCPUs do not enter the BOOST state which is the concern of the proposed algorithms.

Fig. 9(b) compares the *approximate* I/O bandwidth for read and write operations achieved by seven concurrent domains before and after the improvements, each running our Disk I/O benchmark, dd command. In contrast to the compute-bound workloads, we can see some positive impact on the fairness in utilizing the I/O-bandwidth resources among the domains. Not surprisingly, I/O-intensive tasks will incur a large amount of Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

BOOST VCPUs, providing our algorithms with opportunities to perform optimizations.

Given these results, we can conclude that XCollOpts not only optimizes the I/O virtualization for latency-sensitive applications, but it also incurs small or even positive impact on the fairness for other workloads. These results can be further used to show, in an indirect way, the performance behaviors of endto-end applications that combine different computation patterns with respect to the XCollOpts optimizations. Therefore, the enhanced scheduler would have no limitation in practical uses.

#### *E. System Overhead*

The improvements of XCollOpts to the Xen network I/O virtualizations clearly introduce some overheads as both the algorithms and the optimized mechanisms are implemented in both the driver domain and the hypervisor which are frequently executed during the VM scheduling and the I/O communications. To measure the overheads on the overall performance of the virtual platform, we first fully exercise the proposed optimizations by running the netperf to maximize the throughput of

![](_page_10_Figure_1.png)

Fig. 8. Comparisons on CPU and memory utilization of Dom0 before and after the optimization.

the eight domains while measuring the utilization of the processor and the memory of Dom0. Then, we define the system overhead of the optimization as Overhead sys = 1 − t∈[i,j] ηb(t)/- t∈[i,j] ηa(t) where ηb(t) and ηa(t) represent the utilization of CPU or memory at time t before and after the optimization, and [i, j] denotes the experiment time interval when the system is relatively stable.

Fig. 8 shows the compared results of 20s on both CPU and memory utilization before and after the optimizations. Based on these results, we can compute the processor overhead which is approximately 10.06% and the memory overhead which is approximately 0.40%. These overheads are consistent with our expectation since the most parts of the optimizations are computation related.

#### VII. RELATED WORK

As the Credit algorithm is the most frequently used algorithm for the scheduler in Xen-based virtual machines, it has inspired great research interests in both academia and industry [5], [10], [11], [13], [19]. We will view some related work as per main research interests in the literature.

## *A. Computation-Centric Studies*

Cherkasova *et al.* [5] analyze the impact of the disk access speed, network throughput and CPU allocation precision. Chen *et al.* [13] propose a novel way to improve the Credit scheduler to be more adaptive for pinned applications, which can dynamically scale the context switching frequency. The key technique of their solution is variable time slice and behavior analysis.

In contrast, Lange *et al.* [20] show how careful use of hardware and VMM features enable the virtualization of a large-scale HPC (High-Performance Computing) system. The essence of their techniques is to keep the virtual machine as true to the physical machine as possible in terms of its communication and timing properties.

Zhuravlev *et al.* [21] discuss the issue of different classification schemes for scheduling algorithms in multicore processors. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

![](_page_10_Figure_11.png)

Fig. 9. Impact of the enhanced Credit scheduler on CPU and disk IO. (a) CPU utilization. (b) Throughput.

The scheduling algorithms they implement aim to allocate applications among the cores such that the miss rate is spread evenly. Our optimizations are different from theirs as we try to balance the number of VCPUs on each PCPU, instead of the applications directly.

# *B. I/O-Centric Studies*

In contrast to the aforementioned computing-centric studies, Chiang *et al.* [19] propose a management system TRACON to solve the performance effects of co-located data-intensive applications in virtualized environments. TRACON mitigates the interference from concurrent data-intensive applications and greatly improves the overall system performance.

Another related work related to I/O optimizations is [11] where Kim *et al.* present a task-aware VM scheduling mechanism for improving the performance of I/O-bound tasks within a VM. The main goal of their research is to improve the responsiveness of I/O-bound tasks selectively from the CPUbound workloads with complete CPU fairness. This is different from our target domain where latency-sensitive applications are the concern, which are more network related.

Unlike the previous studies, L. Cheng and C. Wang [22] propose *vBalance* to improve I/O performance for SMP virtual machines by using interrupt load balancing. However, *vBalance* is a cross-layer software solution that needs the guest OS to dynamically and adaptively migrate the interrupts from a preempted VCPU to a running one for minimizing the interrupt processing delay. Clearly, this solution is not a pure hypervisor solution adopted by XCollOpts. Gordon *et al.* [23] also propose a software-only approach for handling interrupts within guest virtual machines directly and securely. Similar to the idea of [24], they remove the host from the interrupt handling path to improve the throughput and reduce the latency of unmodified, untrusted guests even for the most demanding I/O-intensive workloads. XCollOpts distinguishes itself from this work in two aspects. We not only consider the interrupt optimizations for latency-sensitive tasks but also investigate the load balancing in multicores and the effectiveness of the tasklet dispatch as well. Therefore, XCollOpts is a more holistic optimization.

#### *C. Latency-Centric Studies*

It has long been recognized that the Credit scheduler exhibits unacceptable performance for I/O-latency sensitive workloads, and the studies on this aspect have a history. As early as 2008, Ongaro *et al.* [10] explored the relationships between domains scheduling in a VMM and I/O performance, and found that when the latency-intensive domains are introduced, the Credit scheduler can provide mixed results, depending on the particular configurations. Later, Dunlap [25] identified some of the design flaws of the Credit scheduler, namely Credit1, and proposed a new design with an attempt to address two issues: one is the load balancing algorithm since the Credit1 does not scale well to a larger number of cores; the other is to well handle the latency-sensitive loads. As such, this work is highly related to our studies, and it is worthwhile to compare them in detail.

To reach the goals, a new algorithm Credit2 was proposed in [25] which is characterized by one runqueue per L2 cache, rather than one runqueue per logical processor to improve the effective use of the processor caches, and the manipulation of the reset event to control the rate at which credit is introduced into the system.

In contrast to the optimization in Credit2, XCollOpts adopts a quite different approach. It considers the issues not only in the Credit scheduler but also in the Xen I/O virtualization. For example, XCollOpts considers the load balancing on BOOST domains instead of the global balancing [25]. On the other hand, it addresses the premature preemption issues in Xen's I/O model, As for the I/O virtualization, XCollOpts also optimizes the data communication mechanisms in terms of the tasklet pairs and data-packet sizes. All of these are not considered in [25]. Therefore, compared to [25], XCollOpts is not a purely scheduler-based solution. Instead, it is a holistic solution, and thus we believe it would have potential values to design other Xen-based software such as the virtual network middleboxes that leverage the NFV technologies.

#### VIII. CONCLUSION AND FUTURE WORK

In this paper, we presented XCollOpts, a collection of novel optimizations to improve the virtual network performance for I/O-latency sensitive applications on multicore systems. This optimization consists of two major parts that are motivated by the observations on the performance flaws in the current Xen implementations. One is at the strategy level where two optimization algorithms, the load balancing of the BOOST Domains and the prevention of the premature preemption, are designed to improve the Credit scheduler to mitigate the adverse impact of the identified IMB and PP problems on the latencysensitive applications. The other is at the mechanism level where we also proposed two optimizations on the underlying virtualized network I/O system for overall throughput improvements. The first is called MTP, which is designed to overcome the performance bottleneck incurred by the single tasklet pair that is shared by all the communicating domains in a machine. The second is designed to improve the existing mechanism to efficiently deliver the small data packets, which is critical to the throughput of the latency-sensitive applications. Our empirical results show that with marginal system overheads, the proposed optimizations can remarkably boost the performance of the latency-sensitive applications with minimized the response time and improved throughput.

Although the XCollOpts optimization is promising, there is still some room left to be explored for further improvements. For example, we only considered the case where there is only one core per VM. Therefore, the efficiency according to the number of VCPUs with BOOST priority when it is larger or smaller than the number of PCPUs is another interesting problem. On the other hand, the comprehensive performance comparison based on the end-to-end applications with the stateof-the-art I/O virtualization such as those with interrupt remapping and re-direction methods [22], and/or SR-IOV capable network devices [24], [26], [27] which are well and largely studied recently, is also desired.

#### ACKNOWLEDGMENT

The authors from Canada are supported by the funding provided to the Centre for Advanced Studies—Atlantic from IBM Canada and the Atlantic Canada Opportunities Agency through the Atlantic Innovation Fund. We also thank the anonymous reviewers whose comments significantly improve the quality of this paper.

#### REFERENCES

- [1] Vmware, VMware, Inc. Singapore, Jan. 2013. [Online]. Available: http:// www.vmware.com/
- [2] Virtual PC, Microsoft, Feb. 2013. [Online]. Available: http://www. microsoft.com/windows/virtual-pc/
- [3] P. Barham *et al.*, "Xen and the art of virtualization," in *Proc. 19th ACM SOSP*, New York, NY, USA, 2003, pp. 164–177.
- [4] Credit Scheduler, 2012. [Online]. Available: http://wiki.xenproject.org/ wiki/Credit_Scheduler
- [5] L. Cherkasova, D. Gupta, and A. Vahdat, "Comparison of the three CPU schedulers in Xen," *ACM SIGMETRICS Perform. Eval. Rev.*, vol. 35, no. 2, pp. 42–51, Sep. 2007.
- [6] L. Zeng, Y. Wang, W. Shi, and D. Feng, "An improved xen credit scheduler for I/O latency-sensitive applications on multicores," in *Proc. Int. Conf. CloudCom-Asia Big Data*, Dec. 2013, pp. 267–274.
- [7] J. Martins *et al.*, "Clickos and the art of network function virtualization," in *Proc. 11th USENIX Conf. NSDI*, 2014, pp. 459–473. [Online]. Available: http://dl.acm.org/citation.cfm?id=2616448.2616491
- [8] S. Lo, M. Ammar, E. Zegura, and M. Fayed, "Virtual network migration on real infrastructure: A planetlab case study," in *Proc. IFIP Netw. Conf.*, Jun. 2014, pp. 1–9.
- [9] S. Govindan, A. R. Nath, A. Das, B. Urgaonkar, and A. Sivasubramaniam, "Xen and Co.: Communication-aware CPU scheduling for consolidated Xen-based hosting platforms," in *Proc. 3rd Int. Conf. VEE*, San Diego, CA, USA, 2007, pp. 126–136.
- [10] D. Ongaro, A. L. Cox, and S. Rixner, "Scheduling I/O in virtual machine monitors," in *Proc. 4th ACM SIGPLAN/SIGOPS Int. Conf. VEE*, Seattle, WA, USA, Mar. 2008, pp. 1–10.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:06:58 UTC from IEEE Xplore. Restrictions apply.

- [11] H. Kim, H. Lim, J. Jeong, H. Jo, and J. Lee, "Task-aware virtual machine scheduling for I/O performance," in *Proc. ACM SIGPLAN/SIGOPS Int. Conf. VEE*, Washington, DC, USA, Mar. 2009, pp. 101–110.
- [12] G. Liao, D. Guo, L. N. Bhuyan, and S. R. King, "Software techniques to improve virtualized I/O on multicore platforms," in *Proc. 4th ACM/IEEE Symp. ANCS*, San Jose, CA, USA, 2008, pp. 161–170.
- [13] H. Chen, H. Jin, K. Hu, and J. Huang, "Dynamic switching-frequency scaling: Scheduling pinned domain in Xen VMM," in *Proc. 39th ICPP*, San Diego, CA, USA, Sep. 2010, pp. 287–296.
- [14] Y. Hu, X. Long, J. Zhang, J. He, and L. Xia, "I/O scheduling model of virtual machine based on multi-core dynamic partitioning," in *Proc. 19th ACM Int. Symp. HPDC*, New York, NY, USA, 2010, pp. 142–154.
- [15] S. Yoo, K.-H. Kwak, J.-H. Jo, and C. Yoo, "Toward under-millisecond I/O latency in Xen-ARM," in *Proc. 2nd APSys Workshop*, 2011, p. 14.
- [16] C. Fraleigh, F. Tobagi, and C. Diot, "Provisioning ip backbone networks to support latency sensitive traffic," in *Proc. 22nd IEEE INFOCOM*, Mar. 2003, vol. 1, pp. 375–385.
- [17] Netperf benchmark. Netperf, Feb. 2013. [Online]. Available: http://www. netperf.org/netperf
- [18] Lookbusy: A Synthetic Load Generator, Open Source Development Labs, Feb. 2013. [Online]. Available: http://www.devin.com/lookbusy/
- [19] R. C. Chiang and H. H. Huang, "TRACON: Interference-aware scheduling for data-intensive applications in virtualized environments," in *Proc. Int. Conf. High Perform. Comput., Netw., SC*, Nov. 2011, pp. 1–12.
- [20] J. Lange *et al.*, "Minimal-overhead virtualization of a large scale supercomputer," in *Proc. ACM SIGPLAN/SIGOPS Int. Conf. VEE*, Newport Beach, CA, USA, Mar. 2011, pp. 169–180.
- [21] S. Zhuravlev, S. Blagodurov, and A. Fedorova, "Addressing shared resource contention in multicore processors via scheduling," in *Proc. 15th Int. Conf. ASPLOS*, Pittsburgh, PA, USA, Mar. 2010, pp. 129–142.
- [22] L. Cheng and C.-L. Wang, "vBalance: Using interrupt load balance to improve I/O performance for SMP virtual machines," in *Proc. 3rd ACM SoCC*. New York, NY, USA, 2012, pp. 1–14.
- [23] A. Gordon *et al.*, "ELI: Bare-metal performance for I/O virtualization," *SIGPLAN Notices*, vol. 47, no. 4, pp. 411–422, Mar. 2012.
- [24] H. Guan, Y. Dong, K. Tian, and J. Li, "SR-IOV based network interruptfree virtualization with event based polling," *IEEE J. Sel. Areas Commun.*, vol. 31, no. 12, pp. 2596–2609, Dec. 2013.
- [25] G. W. Dunlap, "Scheduler development update," Citrix Syst. R&D Ltd., Cambridge, U.K., Tech. Rep., 2010.
- [26] J. Jose *et al.*, "SR-IOV support for virtualization on InfiniBand clusters: Early experience," in *Proc. 13th IEEE/ACM Int. Symp. CCGrid*, May 2013, pp. 385–392.
- [27] G. K. Lockwood, M. Tatineni, and R. Wagner, "SR-IOV: Performance benefits for virtualized interconnects," in *Proc. Annu. Conf. XSEDE*, New York, NY, USA, 2014, pp. 1–7.

![](_page_12_Picture_18.png)

currently with Wuhan National Lab for Optoelectronics, and School of Computer, HUST, as an Associate Professor. He has published more than 40 papers in major journals and conferences.

![](_page_12_Picture_20.png)

**Yang Wang** received the B.Sc. degree in applied mathematics from the Ocean University of China in 1989, and the M.Sc. and Ph.D. degrees in computer science from Carleton University in 2001 and the University of Alberta, Canada, in 2008, respectively. He was with the Department of Electrical and Computer Engineering, National University of Singapore (2010–2012), and IBM Centre for Advanced Studies-Atlantic, University of New Brunswick, Canada (2012–2014). He is now a Professor at the Shenzhen Institute of Advanced Tech-

nology (SIAT), Chinese Academy of Science, China. His research interests include cloud computing, big data analytics, and Java Virtual Machine on multicores. He is an Alberta Industry R&D Associate (2009–2011), and a Canadian Fulbright Fellow (2014–2015).

![](_page_12_Picture_23.png)

**Dan Feng** (M'05) received the B.E., M.E., and Ph.D. degrees in computer science and technology from Huazhong University of Science and Technology (HUST), China, in 1991, 1994, and 1997, respectively. She is a Professor and Vice Dean of the School of Computer, HUST. Her research interests include computer architecture, massive storage systems, and parallel file systems. She has over 80 publications in journals and international conferences, including FAST, ICDCS, HPDC, SC, ICS, and ICPP. Dr. Feng is a member of ACM.

![](_page_12_Picture_25.png)

**Kenneth B. Kent** received the B.Sc. degree from Memorial University of Newfoundland, Canada, and the M.Sc. and Ph.D. degrees from the University of Victoria, Canada. He is a Professor in the Faculty of Computer Science at the University of New Brunswick, and the Director of IBM Centre for Advanced Studies-Atlantic, Canada. His research interests are hardware/software co-design, virtual machines, reconfigurable computing, and embedded systems. His research groups have been key contributors to widely used software, such as the J9 Java

virtual machine and the VTR (Verilog-To-Routing) FPGA CAD flow.

