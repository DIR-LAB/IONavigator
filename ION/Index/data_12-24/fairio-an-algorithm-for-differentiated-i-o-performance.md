# FAIRIO: An Algorithm for Differentiated I/O Performance

Sarala Arunagiri, Yipkei Kwok, Patricia J. Teller, and Ricardo Portillo University of Texas-El Paso, Dept. of Computer Science {sarunagiri@, ykwok2@miners., pteller@, raportil@miners.}utep.edu

Seetharami R. Seelam IBM T.J. Watson Research Center, USA sseelam@us.ibm.com

*Abstract***—Providing differentiated service in a consolidated storage environment is a challenging task. To address this problem, we introduce FAIRIO, a cycle-based I/O scheduling algorithm that provides differentiated service to workloads concurrently accessing a consolidated RAID storage system. FAIRIO enforces proportional sharing of I/O service through fair scheduling of disk time. During each cycle of the algorithm, I/O requests are scheduled according to workload weights and disk-time utilization history. Experiments, which were driven by the I/O request streams of real and synthetic I/O benchmarks and run on a modified version of DiskSim, provide evidence of FAIRIO's effectiveness and demonstrate that fair scheduling of disk time is key to achieving differentiated service. In particular, the experimental results show that, for a broad range of workload request types, sizes, and access characteristics,** *the algorithm provides differentiated storage throughput that is within 10% of being perfectly proportional to workload weights; and, it achieves this with little or no degradation of aggregate throughput***. The core design concepts of FAIRIO, including service-time allocation and history-driven compensation, potentially can be used to design I/O scheduling algorithms that provide workloads with differentiated service in storage systems comprised of RAIDs, multiple RAIDs, SANs, and hypervisors for Clouds.**

# I. INTRODUCTION

The availability of high-speed networks, high-performance storage systems, and virtualization technologies has enabled large computing systems to consolidate storage resources. Storage consolidation offers several advantages over decentralized storage including higher maintainability and lower operational costs. However, when multiple workloads concurrently share the same storage utility, the I/O characteristics of one can degrade the performance of others. Therefore, it is important to provide I/O performance isolation, i.e., provide each concurrently active workload with I/O performance similar to that achievable with a dedicated storage utility of a certain fixed capacity. This guarantees each competing workload a share of storage service, and when shares are proportional to weights assigned to the workloads, the storage system provides *differentiated service* as well.

This paper presents FAIRIO, a RAID I/O scheduling algorithm, and demonstrates its effectiveness. Experimental evidence shows that, for a range of workload request types, sizes, and access characteristics, FAIRIO provides differentiated storage throughput that is within 10% of being perfectly proportional to workload weights, with little or no degradation of aggregate throughput. The algorithm is presented in Section II.

![](_page_0_Figure_8.png)

Fig. 1. RAID Storage System: FAIRIO is assumed to operate at the I/O driver level of the RAID storage hierarchy.

![](_page_0_Figure_10.png)

Fig. 2. FAIRIO service share allocation for each active class.

A description of the experimental environment used to assess the efficacy of FAIRIO and experimental results are presented in Sections III and IV, respectively. The paper concludes with a discussion of related work, conclusions, and future work.

# II. FAIRIO

FAIRIO is designed for RAID storage systems such as the one schematically depicted in Figure 1, and is assumed to be implemented at the I/O driver in order to provide proportional

![](_page_0_Picture_17.png)

| TABLE I |  |
| --- | --- |
| SUMMARY: TERMINOLOGY OF FAIRIO ALGORITHM (DISK TIME IS THE SERVICE METRIC.) |  |
| Scheduler Environment |  |
| wi, W, r | Weight of Classi; sum of weights; number of full scheduling cycles in a window |
| Cyclelength | Amount of wall-clock time in a full scheduling cycle |
| Servicecycle | Amount of service in a full scheduling cycle |
| Servicewindow | Amount of service in a window of observation |
| Service Accounting |  |
| ServiceU tilizedi | Service utilization of Classi in the previous cycle |
| W indowU tilizationi | Service utilization of Classi in the last window |
| ServiceDeviationi | For the last window, deviation of Classi from its rightful share of service |
| T otalDeviation | Sum of service deviations of all active classes |
| T otalUnderService | Sum of service deviations of all under-serviced active classes |
| Service Allocation |  |
| ServiceSharei | Computed (allocated) share for Classi for the current cycle |
| Crediti | ServiceSharei translated to an estimated number of I/O requests |

sharing of the RAID's bottleneck device, the disks. It is a cycle-based algorithm that provides to each concurrentlyactive workload a *proportionate share* of the total available I/O service, i.e., an allocation that is relatively proportional to the workload's weight (a wi/W service share, where wi is workloadi's weight and W is the sum of the weights of all workloads). This is accomplished over a sequence of scheduling cycles via coordinated service-share allocations to *active workloads*, those expected to generate I/O requests. The details of the algorithm are presented in the next four subsections. Table I summarizes FAIRIO terminology.

# *A. Key Concepts*

The design and configuration of FAIRIO involves the definition of the: (1) service metric, which is used to allocate and regulate I/O service; (2) Cyclelength, the wall-clock duration of a full scheduling cycle; (3) Servicecycle, the amount of I/O service in a full scheduling cycle; and (4) window of observation, a moving window of time used in auditing workload service-utilization histories. Each is discussed below.

**Service metric**. A popular service metric used to allocate and regulate I/O service is throughput in terms of either number of bytes or I/O operations. However, even on single-disk systems it is challenging to regulate disk usage via throughput shares because I/O requests are not preemptable and the time required to service them is partially non-deterministic and can vary by orders of magnitude [1]. Thus, both number of bytes per second (B/s) and I/O operations per second (IOPS) are unsuitable metrics for FAIRIO; they do not readily permit guaranteed service shares. The only other available metric is disk time.

As shown in [1], compared to B/s or IOPS, the use of disk time can produce greater control, more efficient use of disk resources, and better workload isolation. In addition, [2] shows the limitations of using B/s or IOPS as a metric in scheduling algorithms designed to provide performance isolation in single-disk systems. Note, however, that a guaranteed disk-time share may not, in general, translate to a guaranteed throughput share because two workloads with equal disk-time shares may receive different B/s or IOPS. This is due to the different costs of I/O requests and intra-disk scheduling decisions that may cause requests to be processed in an order deemed to maximize aggregate throughput.

On the bright side, previous work [3], [1] indicates that for some workloads a guaranteed I/O service share can translate to a throughput guarantee. This is based on the fact that, although potentially difficult to specify generally, applications that require I/O service guarantees often have known I/O behaviors, e.g., multimedia applications have highly sequential access patterns, while high-performance scientific applications have highly regular access patterns. Thus, if an application's I/O behavior and the RAID's performance characteristics are known a priori, then, by providing proportional I/O disk-time service to workloads, FAIRIO can be expected to provide proportional I/O throughput. Accordingly, the metric used by FAIRIO to allocate and regulate I/O service is disk time.

**Cycle length**. Since FAIRIO is a cycle-based scheduling algorithm, the cycle length in terms of wall-clock time is an important parameter, which may affect its performance. Long cycle lengths make it more difficult to deliver proportional service for certain kinds of workloads, especially those with varying request characteristics. On the other hand, although short cycle lengths can be beneficial, they increase FAIRIO's overhead and for workloads with fixed request characteristics more frequent adjustments to service shares may not be necessary. Since FAIRIO allocates service shares at the beginning of each cycle, long (short) cycle lengths decrease (increase) the number of opportunities to adjust service shares. We developed a heuristic that, given a workload, selects a Cyclelength that leads to low errors in terms of proportional service. In addition, we conducted experiments that demonstrate its effectiveness. However, due to space constraints, neither is presented here; they can be found in [4].

**Service cycle**. Once the value of Cyclelength is chosen, then Servicecycle, the amount of I/O service available in a full scheduling cycle, can be computed. Since disks in a RAID operate concurrently, the total amount of disk time available in a scheduling cycle is

$$Services_{cycle}=Cycle_{length}*NumDisks,$$

where NumDisks is the number of disks in the RAID. For example, a RAID with two disks provides twice the amount of disk-time service in a cycle than does a single-disk system.

**Window of observation**. Because of variability in request characteristics, request streams, and storage state across cycles, there generally will be a difference between the service allocated to a workload and the service it actually utilizes. Therefore, in order to maintain differentiated service, the allocation of shares in a cycle factors-in not only workload weights but also observed deviations during a set of previous cycles, called a *window of observation*. Specifically, this is a moving window of time that approximates Cyclelength ∗ r, where r is a FAIRIO parameter that defines the number of full scheduling cycles in a window. A window is approximated by this amount of wall-clock time because it often is composed of a mix of both full and short cycles, the latter being scheduling cycles that were preemptively cut-short to improve performance (see fast-forwarding in Section II-C). As the algorithm proceeds, the window moves, adding the most recent cycle and deleting zero or more from the beginning. Concordantly, the amount of available service in a window, Servicewindow, approximates Servicecycle ∗ r. When FAIRIO is initialized and when workloads join or leave the active set, there is no history of the service utilization of the current active set of workloads. Subsequently, i.e., for at least the next r cycles, there is insufficient history. In such situations FAIRIO assumes a hypothetical window of observation in which Servicewindow is apportioned perfectly proportionately among the workloads.

For simplicity, the following discussion focuses on the algorithm's operation during scheduling cycles that do not use a hypothetical window of observation. In addition, for consistency with the terminology in the literature, a workload is defined as a request class, Classi, a set of I/O requests that are assigned a service allocation weight.

# *B. Service Share Allocation and Request Dispatch*

At the beginning of each scheduling cycle, for each active class, Classi, FAIRIO executes Steps 1 through 4 to allocate service shares and enable request dispatch. Request dispatch is triggered by the events described in Step 5, which can occur any time during a cycle.

**Step 1**. To account for the service utilized by Classi during a cycle, ServiceU tilizedi is transformed to a contextdependent value of utilization or *effective disk-time utilization*, which depends on the actual disk time utilized during the cycle and the state of the storage system.

- If the actual disk time utilized in the cycle by Classi was less than its allocated disk-time share, ServiceSharei, and it had no pending requests in the I/O driver or RAID, ServiceU tilizedi is set equal to ServiceSharei. In this case, because of its own behavior and not that of the algorithm or other classes, Classi was not able to use all of its disk-time allocation. Accordingly, we *do not* compensate for this illusory loss via enabling an increase in future disk-time shares.
- If the actual disk time utilized by Classi during the cycle was greater than ServiceSharei and there was no other active request class with pending requests in the I/O driver or RAID that used less than its disk-time share, ServiceU tilizedi is set equal to ServiceSharei. In this case, Classi used spare disk time − disk time that no

other request class was able to use. As a result, Classi is assumed to have used only its disk-time share and is not penalized for this gain of disk time via decreases in future disk-time shares.

As mentioned earlier, corresponding to every cycle there is a new window of observation. Thus, once ServiceU tilizedi is computed for the previous cycle, W indowU tilizationi, the service utilized by Classi in the last window, is computed as the sum of ServiceU tilizedi over all scheduling cycles that belong to the window of observation. Note that although this sum may not exactly reflect the actual over- or underutilization of the disk-time shares allocated to Classi during the window, it does represent the effective disk time utilized during the window of observation.

**Step 2**. Compute ServiceDeviationi, the difference between W indowU tilizationi and its proportionate share of Servicewindow.

**Step 3**. Determine ServiceSharei, i.e., Classi's service share for the current cycle. The method used to compute ServiceSharei is driven by the prior service utilization of the classes. If there are classes that used less than their rightful shares, the algorithm focuses on compensating each of them with an additional share (Compensation Mode allocation). Otherwise, if all classes used their rightful shares or more, each is given a weight-based share or is penalized, respectively (Proportional Mode allocation). In either case, FAIRIO makes aggressive allocation choices to restore proportionality of service as quickly as possible. Details for these two allocation modes follow and are depicted graphically in Figure 2.

*Compensation Mode*: Used when at least one active class has ServiceDeviation < 0, i.e., it utilized less than its proportionate share of Servicewindow. Since the goal of this mode of allocation is to permit all under-serviced classes to "catch up", the following allocation rules are used; they allocate a relatively larger share of Servicecycle to all underserviced classes and allocate no service to all others.

- 1) Rule 1: If ServiceDeviationi >= 0, allocate Classi no service, i.e., ServiceSharei = 0.
- 2) Rule 2: If ServiceDeviationi < 0, i.e., Classi utilized less than its share of Servicewindow, share Servicecycle among the classes in this state so that each gets a share that is proportionate to its degree of under-service relative to that of all under-serviced classes. Accordingly,

$$ServiceShare_{i}=\frac{|ServiceDeviation_{i}|}{|TotalUnderService|}*Service_{cycle},$$. 

where T otalUnderService is the sum of the ServiceDeviations of all the under-serviced classes.

*Proportional Mode*: Used when all active classes have ServiceDeviation >= 0, i.e., each class utilized either more than its proportionate share of Servicewindow or exactly its proportionate share. Since the goal is to permit the overserviced classes to approach (from above) their proportionate shares, while maintaining the work-conserving nature of the algorithm, the following allocation rules are enforced:

- 1) Rule 1: If for all i ServiceDeviationi > 0, share Servicecycle among all classes so that each gets a share that is inversely proportional to its ServiceDeviation. Thus,
ServiceSharei = 1/ServiceDeviationi T otalDeviation ∗Servicecycle,

where

$$Total Deviation=\sum_{i}(1/Service Deviation_{i}).$$

- 2) Rule 2: If there is at least one class i with ServiceDeviationi = 0 then
- If ServiceDeviationi > 0, allocate Classi no service, i.e., ServiceSharei = 0;
- If ServiceDeviationi = 0, proportionately share Servicecycle among the classes in this state. Thus,

$$ServicesShare_{i}=(w_{i}/W_{p})*Service_{cycle},$$

where Wp is the sum of the weights of the classes in this state.

**Step 4**: Translate ServiceSharei to Crediti, the maximum number of requests that could be dispatched in the current cycle.

$Credit_{i}=ServiceShare_{i}/TimePerRequest_{i}$. 

where T imeP erRequesti is the average observed disk time utilized per request for Classi during the previous cycle. In the special case where no prior cycle exists, Crediti is based on the achievable RAID bandwidth and the expected average request size of the class (a default or input value).

**Step 5**: Dispatch as many as Crediti I/O requests. FAIRIO attempts to dispatch a request to the RAID controller when one of two events occurs: (1) a new request arrives (and is added to the unified pending request queue) or (2) the servicing of a request completes. Note that these events could occur any time during a cycle. Requests are dispatched from oldest to newest. A request of Classi is dispatched only if Crediti > 0; when dispatched, Crediti is decremented and when the servicing of the request completes, the disk time utilized by Classi during the cycle, ServiceU tilizedi, is incremented accordingly. If ServiceU tilizedi ≥ ServiceSharei, the remainder of Classi's credits (for this cycle) are revoked, i.e., Crediti is set to zero. The cycle ends when Cyclelength time has elapsed. Accordingly, some dispatched requests are likely still being serviced and are not reflected in the ServiceU tilizedi value.

# *C. Performance Optimizations*

FAIRIO employs three techniques that target high throughput, while maintaining performance differentiation. The first enforces a minimum threshold, Classthreshold, for the number of requests of a class that can be dispatched in a cycle. If this minimum cannot be met, then (1) no requests of Classi are dispatched in the cycle − request dispatch is deferred to the next cycle when the minimum can be dispatched; and (2) the disk-time share of Classi is distributed among the other active

classes with more than Classthreshold requests in proportion to their service shares.

The second optimization, *fast-forwarding*, terminates the current cycle prematurely and starts a new one when (1) the storage system is under-loaded, i.e., the number of requests in the storage system is below a predefined threshold, StorageLoadthreshold; (2) FAIRIO is unable to dispatch any requests; or (3) there are pending requests that belong to classes that might potentially get credits in the next cycle.

The third optimization is used when there are no eligible requests for FAIRIO to dispatch – FAIRIO maintains a count of the number of such failed attempts. At the end of each cycle, if the total number of requests in the storage system is less than StorageLoadthreshold, FAIRIO attempts to dispatch a batch of requests. Assuming that there are enough credits, the number of requests dispatched is bounded by the smaller of (1) the number of failed dispatch attempts and (2) the minimum number of requests required to change the storage system's state from under-loaded to one where the number of requests in the system is equal to StorageLoadthreshold. In this situation, the number of failed attempts is decremented for each dispatched request.

# *D. Latency Considerations*

Currently, FAIRIO is targeted at throughput-sensitive workloads, for example: (1) asynchronous massively independent workloads [5] such as highly data-parallel scientific (data analysis and visualization) applications that consume large amounts of data and, thus, are more sensitive to throughput than latency; (2) Cloud computing serviced workloads, like Web 2.0 internet applications, which are highly throughputsensitive and latency-tolerant [5]; (3) highly-distributed programming frameworks (for example, Hadoop or MapReduce); and (4) supporting file systems (GFS, for instance), which are designed to run highly latency-insensitive workloads such as web indexing, data mining, log file analysis, and machine learning [6]. Although the current version of FAIRIO does not explicitly enforce defined I/O request latency guarantees, given a well-provisioned storage system and well-behaved workloads, it can be expected to, at least, not negatively impact request latencies. In this case, it may even improve them. Our future work will extend the algorithm to provide best effort latency guarantees as an additional goal.

# III. EXPERIMENTAL ENVIRONMENT

FAIRIO's performance is evaluated using simulations conducted on an enhanced version of DiskSim [7]. In this section, we describe the enhancements, simulated I/O subsystem, benchmarks and traces employed in the evaluation, simulator parameters, and class-weight considerations.

# *A. DiskSim*

We enhanced DiskSim 3.0 to support request classes and implement the FAIRIO algorithm in the I/O driver. DiskSim permits the modeling of caches at both the RAID and disk controllers with a rich set of cache specification parameters (more than 15). Since experimentation with caches at various levels and a large set of parameters is complex, we disabled all caches but the disk controller cache, which models command queuing and, thus, is critical to obtain optimal disk performance. We configure the disk controller cache as a 32-block (16,384-byte) buffer segment.

#### *B. Simulated I/O Subsystem*

The simulated I/O system is similar to the one depicted in Figure 1. As shown, I/O requests from request classes are input to a unified arrival-ordered list of pending requests (tagged with Class IDs) that is used by FAIRIO in determining dispatch order. Each request class is of a specific length and is assigned a particular weight. The I/O driver feeds requests to the RAID controller, which has an FCFS-scheduled queue of "infinite" length – the queue can hold more than the total number of scheduled requests of any experiment. The RAID controller and disks (each modeled as a closed I/O subsystem) are connected via an I/O bus that is used to pass requests, data, and events. An 8-disk RAID-0 configuration is used with IBM model 18es disk drives, each with an SSTF-scheduled request queue that can hold up to 16 requests and a cache of minimal size. We use a RAID-0 configuration because of DiskSim 3.0 limitations. To demonstrate performance differentiation for other RAID levels, FAIRIO needs additional information, e.g., for RAID-5 the time associated with parity computation must be included in the determination of the amount of I/O service available in a scheduling cycle (Servicecycle) and the amount utilized by each request class (ServiceU tilizedi). (Currently, we are investing considerable effort to migrate to DiskSim 4.0 to enable experimentation with other RAID configurations.)

# *C. Benchmarks and I/O Traces*

DiskSim is a trace-driven simulator, thus, suitable I/O traces are needed to drive experiments that can be used to evaluate FAIRIO performance. An I/O request is described by a trace record with the following fields: Class ID, request arrival time (in msecs), disk location (in blocks), request size (in blocks), and access type (read/write). We produced six such traces, three real and three synthetic, using four I/O benchmarks. We ensured that each trace (1) is comprised of multiple request classes, i.e., I/O request streams generated by multiple sources, that cause contention in the modeled shared storage system and (2) consists of enough requests so there is an ample number of cycles to permit FAIRIO to have sufficient opportunities to adjust class shares in order to achieve differentiated service.

For this study, a trace was generated by concurrently executing one instance of a particular benchmark on each of the four compute nodes of a cluster with a shared storage device accessible via a NAS I/O node. Each compute node has dual 2.1GHz quad-core AMD Opterons with 16GB RAM; the NAS I/O node has a 2.3GHz quad-core Intel Xeon and 8GB RAM. All the block I/O requests generated by the four benchmark instances were captured on the I/O node before they were dispatched to the underlying shared storage system. The I/O requests of each instance comprise a request class and, thus, each trace is comprised of the requests of four different classes.

The four I/O benchmarks used to produce the traces are: (1) varmail executed using Filebench as a workload personality, a non-scientific benchmark; (2) NAS BTIO and MADbench2, two scientific benchmarks, and (3) IOR, a synthetic benchmark from Lawrence Livermore National Laboratory, parameterized in three different ways to generate a trace with a random access pattern (for IOR1 experiments); a trace with a sequential access pattern (for IOR2 experiments); and a trace with a mixed access pattern in which Classes 1 and 3 have random access patterns and Classes 2 and 4 have sequential access patterns (for IOR3 experiments). Table II summarizes how each compute-node benchmark instance was configured to produce the I/O traces used in this study.

To generate each trace, we adjust benchmark parameters until the I/O activity in a simulation is theoretically sufficient to consistently backlog the request queues of the disk I/O controllers. For the benchmarks used in this study, we were successful in this endeavor for all but MADbench2. Next, via simulation with FAIRIO disabled, we measure the aggregate delivered throughput of each class in the trace. For all the traces but that of IOR3, which has classes with disparate access patterns, each class received approximately 25% of the aggregate delivered throughput. This is because each of the other traces are generated by executing multiple instances of the same benchmark. Traces with these characteristics, i.e., that generate sufficient I/O activity to backlog the simulated disk controller queues and result in comparatively equal simulated aggregate delivered throughput, provide a baseline performance comparison (with FAIRIO disabled) and permit us to test the efficacy of FAIRIO, while gaining insights into its behavior. In addition, we observed that each trace caused a simulation to run for more than 200 cycles, which permitted FAIRIO a sufficient number of opportunities to adjust class shares in order to achieve differentiated service.

#### *D. Simulator Parameters*

Given an I/O trace, DiskSim services the I/O requests generated by the four instances of the associated I/O benchmark, which concurrently access the modeled shared storage system. Accordingly, we use DiskSim experiments to study the I/O behavior of the system, with and without FAIRIO enabled.

For all DiskSim experiments with FAIRIO enabled, Classthreshold = 1, StorageLoadthreshold = 16, and r = 20. We conservatively set Classthreshold to 1 to avoid starvation; setting it higher can potentially increase throughput. To ensure high bandwidth utilization, StorageLoadthreshold is set to match the capacity of the disk controller queue. We settled on r = 20 since this value showed good overall performance for our experiments. Note, however, that we have observed better performance in terms of disk-time differentiation with other values of r for specific workloads. For example, the error bound for the IOR2 experiment decreases by 3% when r is set to 25 rather than 20. Currently we are investigating how best to tune this window-size parameter given a set of active workloads. Table II lists the values of Cyclelength and the size of the window (20 x Cyclelength) used in the experiments.

Lastly, for each experiment, weights 3, 4, 5, and 6 are assigned to Classes 1, 2, 3, and 4, respectively. This translates to expected throughput shares of 16.7%, 22.2%, 27.8%, and 33.3% for the four classes. The methodology used to assign these weights is discussed in the next section.

# *E. Class-weight Considerations*

Given a set of request classes, FAIRIO can provide differentiated I/O service as well as differentiated delivered throughput, while maximizing aggregate throughput, under the following two ideal conditions.

Condition 1: Ai*, the request arrival rate (B/s) is evenly distributed across cycles and satisfies the following inequality:*

$A_{i}\geq\frac{w_{i}*T}{\sum w_{i}}$ for all $i$, (1)

where wi is the weight of Classi and T is the estimated throughput of the RAID system achievable by the given set of request classes or, as an approximation, the highest throughput achieved by any set of classes.

Condition 2: *The average request disk-time service (s/B), including seek time and rotational latency, for all classes is the same.* This ensures that differentiated service in terms of disk time translates to differentiated delivered throughput.

In an HPC system (with a dedicated RAID storage system) where a set of applications are run repeatedly, T also can be the estimated achievable throughput − this is assessable using performance data collected while running these applications concurrently. Given T , weights that satisfy inequality (1) can be assigned to the request classes associated with the applications. These weights can be used in subsequent runs to ensure that FAIRIO comes close to providing differentiated I/O service, while maximizing aggregate throughput. This is how we determined the class weights for our experiments.

# IV. PERFORMANCE EVALUATION

Although FAIRIO does not promise differentiated delivered throughput, in the end it is the performance metric of consequence in a real I/O system. Thus, for each experiment, below we present and discuss the error in differentiated delivered throughput for each class, Errori , and the aggregate throughput (of all four classes combined) averaged over time. Errori , i ∈ {1, ..., n}, where n is the number of active classes, is defined in terms of Ti, the average throughput (B/s) achieved by requests of Classi during a given interval, and wi, the weight of Classi, i.e.,

Errori = (ActualRatioi − IdealRatioi), where IdealRatioi = wi i(wi) and ActualRatioi = Ti i(Ti) .

In this context, *differentiated delivered throughput* guarantees each competing class a share of throughput that is proportional to its weight.

Figure 3 depicts Errori for each of the four request classes associated with each of the six experiments. The name of an experiment reflects the name of the I/O benchmark that was used to generate the associated I/O trace. The maximum and minimum errors are shown for each experiment and the two values in between are represented by tick marks. In addition, Figure 4 illustrates the aggregate throughput (MB/s) attained by each experiment and compares it to that attained by an analogous experiment with FAIRIO disabled.

#### *A. Results of Experiments Driven by Real I/O Traces*

Experiments with FAIRIO enabled that were driven by real I/O traces resulted in all request classes of all experiments realizing I/O throughput within 7% of being perfectly proportional to their weights. In addition, the aggregate throughput was within 4% of that delivered when FAIRIO was disabled.

As shown in Figure 3, these experiments result in Errori for Classi, i ∈ {1, ..., 4}, that ranges from -0.32% to -6.93%. For each of the four varmail request classes the error is less than 0.5%; for each of the BTIO classes, it is less than 2%; and for each of the MADbench2 classes, it is less than 7%.

In addition, as depicted in Figure 4, these experiments result in aggregate throughputs that are very close to those achieved with FAIRIO disabled. In the worst case (the MADbench2 experiment), the aggregate throughput is 3.3% smaller than that achieved with FAIRIO disabled. And, in the best case (the varmail experiment), it is 0.6% higher.

To evaluate FAIRIO's performance for a wider range of class weights, we conducted an additional varmail experiment with weights 1, 4, 8, and 16. The errors were bounded by 1.7% and there was no degradation of aggregate throughput.

# *B. Results of Experiments Driven by Synthetic I/O Traces*

Experiments with FAIRIO enabled that were driven by synthetic I/O traces, generated using the IOR benchmark, resulted in all request classes of all experiments realizing I/O throughput within 10% of being perfectly proportional to their weights. In addition, the aggregate throughput delivered was higher than that delivered when FAIRIO was disabled.

As shown in Figure 3, these experiments result in Errori , i ∈ {1, ..., 4}, that ranges from 1.5% to 9.95%. For each of the four IOR1 request classes (with random access patterns), the error is less than 1.5%; for each of the IOR2 classes (with sequential access patterns), it is less than 4.5%; and for each of the IOR3 classes (with different access patterns for each pair of classes), it is as high as 9.95%.

In addition, as depicted in Figure 4, these experiments result in aggregate throughputs that are higher than those achieved without FAIRIO. In the worst case (the IOR2 experiment) the achieved aggregate throughput is 0.82% higher than that achieved without FAIRIO. And, in the best case (the IOR3 experiment), it is 14.49% higher. The IOR1 experiment achieved an aggregate throughput 2.98% higher.

# *C. Summary and Analysis of Results*

For the experiments conducted in this study, FAIRIO delivered differentiated throughput to each class within 10%

|  | TABLE II |  |
| --- | --- | --- |
|  | EXPERIMENTAL DETAILS |  |
| Benchmark | Trace Generation: Compute Node Execution Instance | Cyclelength / Window Size |
| varmail | 10-minute execution of Filebench with 12 concurrent threads; emulates the storage accesses of a /var/mail NFS | 1.0/20 secs |
|  | mail server through a specific loadable workload personality |  |
| BTIO | BTIO with problem size Class A and four MPI tasks accessing the same output file; configured to issue a write | 2.2/44 secs |
|  | every three (instead of the default five) time steps |  |
| MADbench2 | MADbench2 with 4, 000 x 4, 000 pixel problem size, four MPI tasks, all of which can issue read and write | 3.1/62 secs |
|  | requests concurrently, and 16 component matrices; gang scheduling disabled and 32-byte file block size |  |
| IOR1, IOR2, | IOR with 12 MPI tasks; writes 64KB requests to a 3GB file; configured to use the POSIX I/O API; performs | 2.1/42, 3.6/72, |
| and IOR3 | fsync after each write, which transfers modified data from the system buffer to storage in order to minimize the | and 1.7/34 secs |

![](_page_6_Figure_1.png)

-6.93

-9.95

varmail BTIO MADbench2 IOR1 IOR2 IOR3 Experiments

-10

Errors (%) 

Fig. 3. Errori, the deviation from perfect differentiated throughput sharing, for the four request classes of each of the six benchmarks. Values between the extremes are represented by tick marks.

![](_page_6_Figure_4.png)

Fig. 4. Aggregate throughput achieved by each of the six experiments compared to that achieved by analogous experiments with FAIRIO disabled.

of being perfectly proportional to its weight. Additionally, FAIRIO provided differentiated I/O service without significantly decreasing aggregate throughput. For all experiments with FAIRIO, the decrease in aggregate throughput was bounded by 3.5%. In four of the six experiments (varmail, BTIO, IOR1, and IOR2), the absolute error in differentiated throughput was bounded by 5%. Below we discuss the IOR3 and MADbench2 experiments, which have errors in the 5-10% range.

For the four IOR3 classes, the error in differentiated disk-

time service was bounded by just 1.5%. However, the error in throughput differentiation was as high as 9.95%. This discrepancy can be explained by analyzing the I/O characteristics of IOR3 in terms of Conditions 1 and 2 (Section III-E), which are FAIRIO prerequisites for perfect differentiated service and throughput. The four IOR3 classes satisfy inequality (1) but violate Condition 2, which states that the average request disktime service (s/B) is the same for all classes. Specifically, the average request disk-time service for random-access classes and sequential-access classes are 1.14 and 0.67 microsecs/B, respectively. Thus, for the IOR3 experiment, although FAIRIO worked as designed and provided differentiated disk-time service with small errors, the differentiation did not map as well to throughput due to the inherent variability of s/B among the IOR3 classes.

On the other hand, MADbench2 satisfies Condition 2 but not 1. Inequality (1) of Condition 1 for MADbench2 (for which T = 11.76 MB/s and A1, A2, A3, and A4 equal 3.04, 2.06, 3.01, and 3.01MB/s, respectively) shows that Classes 3 and 4 fall short of the inequality by a wide margin (Class 2 only negligibly so). Thus, Classes 3 and 4 do not have request rates high enough to consume their disk-time allocations. In turn, this unused disk time was given to Classes 1 and 2, and accounts for 8.20% and 1.81% of their delivered throughputs, respectively. Effectively, this was a scenario where FAIRIO did not waste spare throughput caused by the inherent low consumption of high-weighted classes.

In summary, FAIRIO is designed to provide differentiated service and throughput with minimal error when request classes satisfy Conditions 1 and 2. However, when these conditions are not met, FAIRIO will choose higher throughput over strict adherence to differentiation to avoid wasted I/O disk-time allocations. Accordingly, the results for the IOR3 and MADbench2 experiments illustrate that errors in delivered throughput, used as an isolated metric, do not always reflect the effectiveness of FAIRIO in reaching its objectives. With this is mind, we conclude that FAIRO was effective in balancing differentiated service and storage utilization in all the six experiments.

# V. RELATED WORK

I/O scheduling has been explored extensively and there are a number of contemporary I/O scheduling algorithms that target performance isolation including Cello [8], Fac¸ade [9], Triage [10], SLEDS [11], PARDA [12], Maestro [13], and the 2-Level Interposed Scheduler [14]. Fair queue disk schedulers such as Cello achieve fair sharing of disk I/O to some extent. To do this, Cello requires detailed performance models of the disk system and/or models to estimate seek and rotational delays for each I/O request. Constructing such models is difficult for a single drive, let alone multi-drive disk arrays. And, it is not clear how these schedulers handle devices with controllers that support out-of-order service. Various similar strategies seek to provide QoS management of disk I/O [15], [16], [14] − they use fair queuing and claim to achieve performance virtualization, however, all of them require similar whitebox performance models. I/O scheduling algorithms such as Fac¸ade, Triage, SLEDS, PARDA, and Maestro use feedback mechanisms for admission control and, thus, avoid the need for accurate models. However, they have various drawbacks including the inability to fully exploit the concurrency at the disk controller and, aside from PARDA and Maestro, they are not work-conserving, i.e., they potentially under-utilize spare storage resources. As a result, these algorithms achieve some level of performance isolation but at a cost in terms of storage efficiency. FAIRIO also uses similar feedback mechanisms, avoiding the need for detailed models of the storage device. However, it maintains work conservation by monitoring the system for request class idleness and by adapting request scheduling to eliminate storage device under-loading.

PARDA saves a limited amount of under-utilized credits to take advantage of spatial locality during bursts, which can increase throughput. FAIRIO does not apply this optimization technique because servicing I/O bursts with accumulated under-utilization credits can degrade performance isolation. Maestro provides proportional services and best-effort QoS guarantees to applications sharing large disk arrays. It differentiates itself from the rest of the algorithms by supporting multiple performance requirement metrics, such as throughput and latency, for different applications depending on their nature. Currently, we are working on extending FAIRIO to meet multiple performance objectives, specifically, best-effort latency guarantees in addition to throughput differentiation.

The design of the fairly sophisticated 2-Level Interposed Scheduler [14] is based on statistics and queuing theory. It provides performance isolation as long as the different I/O streams have approximately similar arrival rates. However, in reality request streams typically have diverse access characteristics such as variable run counts or jump distances and FAIRIO maintains isolation in these practical cases where others fail.

#### VI. CONCLUSIONS AND FUTURE WORK

This paper introduced the FAIRIO cycle-based I/O scheduling algorithm that provides differentiated service to request classes concurrently accessing a consolidated RAID storage system. For experiments using synthetic and real workloads, FAIRIO delivered differentiated throughput with less than 10% error and with little or no aggregate throughput degradation.

FAIRIO has various tunable parameters and our future work will explore heuristics to predict their optimal values. In parallel, we are extending the FAIRIO algorithm to provide besteffort latency guarantees. Latency enforcement leads to further challenges such as the balancing of different performance objectives, minimizing the impact of one over another, and analyzing tradeoffs between different objectives. Finally, we plan to use the essence of FAIRIO to develop algorithms for more complex consolidated storage systems and file systems.

#### ACKNOWLEDGMENTS

This work was supported by the Department of Energy, the Office of Science, Joint Mathematics/Computer Science Institute Grant No. DE-SC0001768 and the Army Research Laboratory under the AHPCRC (Army High Performance Computing Center) Grant No. W11NF-07-2-0027.

# REFERENCES

- [1] T. Kaldewey, T. Wong, R. Golding, A. Povzner, S. Brandt, and C. Maltzahn, "Virtualizing disk performance," in *RTAS '08: Proc. of the 2008 IEEE Real-Time and Embedded Technology and Applications Symp.*, 2008, pp. 319–330.
- [2] S. R. Seelam, "Towards dynamic adaptation of I/O scheduling in commodity operating systems," Ph.D. dissertation, The University of Texas at El Paso, 2006.
- [3] A. Povzner, T. Kaldewey, S. Brandt, R. Golding, T. Wong, and C. Maltzahn, "Efficient guaranteed disk request scheduling with fahrrad," *SIGOPS Oper. Syst. Rev.*, vol. 42, no. 4, pp. 13–25, 2008.
- [4] S. Arunagiri, Y. Kwok, P. J. Teller, R. Portillo, and S. R. Seelam, "A heuristic for selecting the cycle length for FAIRIO," Department of Computer Science, The University of Texas at El Paso, Tech. Rep. UTEP-CS-11-53, September 2011.
- [5] L. Ramakrishnan, K. R. Jackson, S. Canon, S. Cholia, and J. Shalf, "Defining future platform requirements for e-science clouds," in *SoCC '10: Proceedings of the 1st ACM Symposium on Cloud Computing*. New York, NY, USA: ACM, 2010, pp. 101–106.
- [6] J. Shafer, "A storage architecture for data-intensive computing," Ph.D. dissertation, Rice University, 2010, advisor-Rixner, Scott.
- [7] J. S. Bucy, G. R. Ganger, and Contributors, "The DiskSim simulation environment version 3.0 reference manual," School of Computer Science, Carnegie Mellon University, Tech. Rep. CMU-CS-03-102, January 2003.
- [8] P. Shenoy and H. Vin, "Cello: a disk scheduling framework for next generation operating systems," University of Texas at Austin, Tech. Rep., 1998.
- [9] C. Lumb, A. Merchant, and G. Alvarez, "Fac¸ade: virtual storage devices with performance guarantees," in *FAST '03: Proc. of the 2nd USENIX Conf. on File and Storage Technologies*, 2003, pp. 131–144.
- [10] M. Karlsson, C. Karamanolis, and X. Zhu, "Triage: performance differentiation for storage systems using adaptive control," *Trans. Storage*, vol. 1, no. 4, pp. 457–480, 2005.
- [11] D. Chambliss, G. Alvarez, P. Pandey, D. Jadav, J. Xu, R. Menon, and T. Lee, "Performance virtualization for large-scale storage systems," in *SRDS '03: Proc. of the 22nd Int. Symp. on Reliable Distributed Systems*, 2003, pp. 109–118.
- [12] A. Gulati, I. Ahmad, and C. A. Waldspurger, "PARDA: proportional allocation of resources for distributed storage access," in *FAST '09: Proc. of the 7th Conf. on File and Storage Technologies*. Berkeley, CA, USA: USENIX Association, 2009, pp. 85–98.
- [13] A. Merchant, M. Uysal, P. Padala, X. Zhu, S. Singhal, and K. Shin, "Maestro: quality-of-service in large disk arrays," in *Proc. of the 8th ACM Int. Conf. on Autonomic Computing*, ser. ICAC '11. New York, NY, USA: ACM, 2011, pp. 245–254.
- [14] J. Zhang, A. Sivasubramaniam, Q. Wang, A. Riska, and E. Riedel, "Storage performance virtualization via throughput and latency control," *Trans. Storage*, vol. 2, no. 3, pp. 283–308, 2006.
- [15] W. Jin, J. Chase, and J. Kaur, "Interposed proportional sharing for a storage service utility," *SIGMETRICS Perform. Eval. Rev.*, vol. 32, no. 1, pp. 37–48, 2004.
- [16] R. Wijayaratne and A. Reddy, "Providing QoS guarantees for disk I/O," *Multimedia Syst.*, vol. 8, no. 1, pp. 57–68, 2000.

