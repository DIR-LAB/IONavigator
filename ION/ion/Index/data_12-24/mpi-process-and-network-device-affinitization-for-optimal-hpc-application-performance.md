# MPI Process and Network Device Affinitization for Optimal HPC Application Performance

Ravindra Babu Ganapathi

Aravind Gopalakrishnan Intel-R Corporation

Russell W Mcguire

Intel-R Corporation Email:ravindra.babu.ganapathi@intel.com Email:aravind.gopalakrishnan@intel.com Intel-R Corporation Email:russell.w.mcguire@intel.com

*Abstract*—High Performance Computing(HPC) applications are highly optimized to maximize allocated resources for the job such as compute resources, memory and storage. Optimal performance for MPI applications requires the best possible affinity across all the allocated resources. Typically, setting process affinity to compute resources is well defined, i.e MPI processes on a compute node have processor affinity set for one to one mapping between MPI processes and the physical processing cores. Several well defined methods exist to efficiently map MPI processes to a compute node. With the growing complexity of HPC systems, platforms are designed with complex compute and I/O subsystems. Capacity of I/O devices attached to a node are expanded with PCIe switches resulting in large numbers of PCIe endpoint devices. With a lot of heterogeneity in systems, applications programmers are forced to think harder about affinitizing processes as it affects performance based on not only compute but also NUMA placement of IO devices. Mapping of process to processor cores and the closest IO device(s) is not straightforward. While operating systems do a reasonable job of trying to keep a process physically located near the processor core(s) and memory, they lack the application developer's knowledge of process workflow and optimal IO resource allocation when more than one IO device is connected to the compute node.

In this paper we look at ways to assuage the problems of affinity choices by abstracting the device selection algorithm from MPI application layer. MPI continues to be the dominant programming model for HPC and hence our focus in this paper is limited to providing a solution for MPI based applications. Our solution can be extended to other HPC programming models such as Partitioned Global Address Space(PGAS) or a hybrid MPI and PGAS based applications. We propose a solution to solve NUMA effects at the MPI runtime level independent of MPI applications. Our experiments are conducted on a two node system where each node consists of two socket Intel-R Xeon-R servers, attached with up to four Intel-R Omni-Path fabric devices connected over PCIe. The performance benefits seen by MPI applications by affinitizing MPI processes with best possible network device is evident from the results where we notice up to 40% improvement in uni-directional bandwidth, 48% bi-directional bandwidth, 32% improvement in latency measurements and finally up to 40% improvement in message rate.

*Keywords*—Fabric, High Performance Computing, Process affinity, MPI, Topology, Infiniband, NUMA, Performance

#### I. INTRODUCTION

HPC systems continue to evolve in complexity with respect to processor, memory and IO devices creating complex NUMA platform architectures [1].

Intel-R provides two main processor solutions- Intel-R Xeon-R and Intel-R Xeon PhiTM processors which are intended for different audiences with diverse needs. Intel-R Xeon PhiTM processors have large number of small cores that are best suited for large massively parallel applications, and Intel-R Xeon-R processors have large powerful cores that provide limited parallelism but efficient in executing complex sequential code. While this provides good choices for different types of application developers, it further complicates platforms architectures and necessitates developer to think about application's affinity and NUMA placement effects.

With the demanding memory requirements of HPC applications, memory has evolved in recent years. Specifically main memory, which was traditionally DRAM, now consists of hierarchical memory with differences in performance and capacity. One example is the combination of high bandwidth MCDRAM memory and DDR present with Intel-R Xeon PhiTM systems.

For data centers with fabric components, Intel-R Omni-Path Architecture (OPA) is designed to integrate seamlessly with CPU and memory components catering to the high performance metrics of low latency and high bandwidth. At the crux of OPA are Host Fabric Interfaces (HFI). HFIs connect each host to the fabric and act as the translation medium for host processor and fabric components. HFIs are concerned with implementing the physical and link layers of the fabric architecture such that the host can perform the basic send and receive functions with peers in the network. A more detailed overview of Intel-R OPA and hardware interfaces is conducted in [2].

IO devices, specifically network devices used in HPC clusters, are typically either Ethernet devices or low latency high bandwidth interconnect such as Intel-R Omni-Path devices or other Infiniband based devices. With the growing demand for higher I/O bandwidth in HPC clusters, systems are often configured with more than one network device per node.

In simple cases there is one network device per node connected over PCIe and all inter-node traffic goes over the single device. This gets cumbersome when more than one network device is attached to the node. These network devices can be either directly connected over PCIe or some of them can be connected over a PCIe switch.

On multi-socket node with multiple IO devices, one or more IO devices can be attached to each CPU socket. Process(es) running on a node communicating with process(es) on remote node(s) using a network device that is attached to the same CPU socket results in better performance than using an IO device that is attached to a different socket. The difference in performance is due to the additional inter-socket communication latency. In this paper we provide a detailed design and algorithms that can be implemented as part MPI runtime to automatically choose the right IO device(s) for optimal performance. Further, we provide additional process configuration options to affinitize multiple IO devices to a process for cases where more than one IO device is needed for communication which is commonly termed as multi-rail.

We verify our functional and performance claims by implementing our solution as part of Intel-R OPA software stack and measuring performance with standard OSU micro-benchmarks (OMB) suite version 3.1.1 benchmarks.

The rest of the paper is organized as follows. We explain design of HFI device affinitization in Section II, which includes system configuration and provides device selection algorithms. Experimental results and the associated analysis for bandwidth, latency and message rate are provided in Section III. Section IV outlines related work and finally we conclude summarizing our findings and describing potential future work in Section V

#### II. DESIGN OF HFI DEVICE AFFINITIZATION

#### *A. Node Configuration*

In this paper, we propose solution to solve multi network device affinity issue to obtain optimal performance. All the experiments described in this paper are conducted with systems containing Intel-R Omni-Path devices. Further, each node is a dual socket Xeon-R server with two PCIe v3.0 slots with 16 lanes each. With this node configuration, we can have up to four Intel-R Omni-Path devices per node. The term Host Fabric Interface (HFI) is also used to refer to Intel-R Omni-Path devices. Therefore, in this paper, we will be using the terms interchangeably.

Following are the three configurations in our experimental system requiring different affinity behavior:

- 1) Single HFI device per node
- 2) Two HFI devices per node, one per socket
- 3) Four HFI devices per node, two per socket

Configuration 1 shown in Figure 1 is the simplest where all MPI traffic flows through the single device on the node.

![](_page_1_Figure_11.png)

Fig. 1. Single HFI per node

Configuration 2 shown in Figure 2 provides three different possible communication pattern for MPI process:

- 1) HFI device local to the socket
- 2) HFI device remote to the socket

- 3) Allow sending traffic over both HFI devices
![](_page_1_Figure_17.png)

Fig. 2. Dual HFI per node, one per socket

Configuration 3 shown in Figure 3 provides five different possible combinations of communication pattern for MPI process:

- 1) One HFI device local to the socket
- 2) One HFI device remote to the socket
- 3) Allow sending traffic over both HFI devices local to the socket
- 4) Allow sending traffic over both HFI devices remote to the socket
- 5) Allow sending traffic over all the devices in the system

![](_page_1_Figure_25.png)

Fig. 3. Four HFI devices per node, two per socket

Configuration 3's communication pattern is a super set of the above three configurations. Hence, our experiments are conducted on system with four Intel-R Omni-Path devices per node, each of these Intel-R Omni-Path devices connected to the same Intel-R Omni-Path Edge switch.

## *B. MPI Process Affinity*

The MPI process affinity depends on several factors. Using application inter-node and intra-node communications characteristics is a common heuristic. [3], [4]. To support user process placement strategies, MPI implementations usually provide their own run-time systems for launching and monitoring individual processes or use a back-end parallel runtime environment. Two widely used mapping patterns are "bynode" and "by-slot" methods. The "by-node" option allows users to place processes in a round-robin fashion among the nodes while "by-slot" performs a similar function among available "slots" (The definition of a slot could vary between different MPI implementations and platforms. Typically, it refers to processor cores or hardware threads). Modern resource managers carry support to allocate resources at core level while older systems provided only allocation support at node granularity.

MPI resource managers first allocate resources to a given MPI job. The mapping agent (provided by either resource manager or the MPI implementation) then creates a map of process to underlying processor cores and memory. This involves a specification of which processes is to be launched on each node and checks to prevent oversubscribing of any hardware resource. After mapping, each process is assigned a unique rank in MPI COMM WORLD. The ordering of ranks is important as it can map the ranks to resources in a roundrobin (natural) format or a sequential format where first N ranks are placed on first node, second set of N ranks on second node and so on. At launch time, the runtime environment works with Operating System (OS) to bind the process to the cores determined from the earlier mapping and ordering phases.

## *C. Device Selection Based On MPI Process Affinity*

Performance Scaled Messaging (PSM2) [5] is the high performance scalable messaging library for Intel-R Omni-Path architecture that matches the semantics needed by MPI. Currently, PSM2 supports up to four HFI devices per node. Therefore, it includes some basic logic to identify available devices in the system and to find out which ones it can use for a given job.

*1) PSM2 Environment Variables:* PSM2 provides environment variables to control the behavior of affinity logic. A full description of PSM2 enviornment variables is beyond the scope of this paper and hence we limit ourselves to describing relevant environment variables used. However, PSM2 source code has been open-sourced and is publicly available on GitHub [5].

- 1) PSM2 MULTIRAIL
- 2) PSM2 MULTIRAIL MAP
- 3) HFI SELECTION ALG

PSM2 MULTIRAIL takes in values ranging from [0,2]. The value of "0" is default behavior which is multi-rail switched off. A value of "1" tells PSM2 to use all available and active HFI(s) in the system for communication. A value of "2" instructs PSM2 to use multi-rail functionality but restrict the selection of HFI(s) to use within the NUMA node of currently running process. In this case, the NUMA node is the PCIe root complex of an Intel-R Xeon-R processor. For discussion in this paper, we enforce values of [1,2] with this environment variable to compare performance with affinity logic or otherwise.

PSM2 MULTIRAIL MAP accepts values in the form unit:port. This is input to PSM2 for selecting HFIs(unit) to use to set up the rails. If only one unit is specified, it is equivalent to a single-rail case. PSM2 parses the input to gather all units which serves as mask to limit multi-rail to the specified HFI(s). Unit values starts from 0 and Port value is always 1 indicating single port HFI. For purposes of experiments in the paper, we use this environment variable for evaluating worst case performance by listing HFIs from the remote socket.

HFI SELECTION ALG accepts arguments such as "Round Robin" and "Packed". Round Robin is the default mode where the job is evenly distributed across the HFI(s) available in the NUMA node. This is also the recommended mode of operation. The "Packed" mode allows user to completely subscribe the hardware contexts available from the first HFI device before moving to assign contexts in the next available HFI. If user prefers to spread job across all available HFI(s) in the system and not restrict to just the NUMA node (which is default), the user can override it by using "Round Robin All" as argument to the environment variable. For discussion in this paper, we allow default operation for this environment variable.

*2) HFI Selection Algorithm:* PSM2 uses a combination of best fit and first fit approaches to select the HFI device to use for a particular process. After PSM2 scans the system looking for all available HFIs, it will first check if all available devices have the maximum number of free contexts. If this is the case, it likely means that no other MPI job is running in the system. Therefore, PSM2 starts looking at the first available HFI in the system and tries to assign a context. If it fails for any reason, it tries next available HFI. In this manner, it keeps trying until one is assigned for current process. In the event that any HFI in the system is not idle, then its available contexts will be less than other HFIs. In this case, since PSM2 cannot reliably determine which HFI would have been chosen for an earlier job, it will try to spread the new job uniformly across all available HFIs in the system. Typically, this results in an uniform distribution of jobs across the HFIs. The user does have ability to manually choose the HFI to use for the job.

In this paper, we propose a modification to the existing default selection algorithm by taking into account the affinity of the MPI process. In the pseudocode (refer Algorithm 1), "hfival" represents the user provided input. If a value has been assigned by user (values greater than 0), we can return early and use the assigned HFI unit. Otherwise, the NUMA node affinity of all available HFIs in the system ("Hnode") is compared with the NUMA node affinity of the currently executing process ("Pnode"). If the values match, the HFI unit number is placed in a saved hfis array. When there is only one HFI on the NUMA node local to the process, we can return the first item in the array. To ensure an uniform distribution of jobs across HFIs in case there are more than 1 HFI on the same local node, we invoke the spread hfi function and return. If no HFIs are found on local NUMA node PSM2 will fall back to finding one on remote node.

*3) Multirail Usage:* For systems where we have more than one HFI devices installed, MPI applications with more than one rank in the job per node will automatically leverage the available HFIs in the system. The user can provide hints to PSM2 using environment variables to help with choosing the correct HFI devices based on the core and NUMA socket on which the rank is placed by the job launcher.

Using the hints provided by the user application, PSM2 will attempt to find available and active HFIs within the same NUMA socket on which the MPI rank is launched. As shown in Algorithm 2, the logic is similar to the previous

|  | Algorithm 1 HFI selection algorithm with affinity constrains |
| --- | --- |
| 1: procedure HFI SELECTION |  |
| 2: | hf ival ← User chosen HFI or -1 |
| 3: | pnode node of current thread() ← numa |
| 4: | ival if hf >= 0 then return hfival |
| 5: | else |
| 6: | activeunits ind active units() ← f |
| 7: | if activeunits = 1 then |
| 8: | hf ival ← 0 return hfival |
| 9: | else |
| 10: | for i = 0;i < availunits;i + + do |
| 11: | hnode ← NUMA node of unit(i) |
| 12: | if hf i active(i) & hnode = pnode then |
| 13: | saved hf is[j++] ← i |
| 14: | end if |
| 15: | end for |
| 16: | if j > 1 then |
| 17: | hf ival hf hf ← spread i(saved is[]) |
| 18: | return hfival |
| 19: | else if j = 1 then return saved hfis[0] |
| 20: | else |
| 21: | hf ival remote node hf ← select i() |
| 22: | return hfival |
| 23: | end if |
| 24: | end if |
| 25: | end if |
| 26: end procedure |  |

HFI selection algorithm. If user requests to use multirail across NUMA nodes ("mrail" value of 1), then we invoke the respective setup utility and return. Else, if request is for Multirail within a NUMA node ("mrail" value of 2), PSM2 will compare the NUMA node affinity of the currently executing thread ("Pnode" value) with the NUMA node affinity of a list of HFIs obtained by probing the system ("Hnode" values). If matching values are found, then HFI unit numbers are added to a saved hfis array. After system probing, each of the devices from the array is independently configured and context is assigned. Protocol level structures are duplicated for communication. With this algorithm, if PSM2 finds at least one HFI in the socket, it will choose to use it.

## III. EXPERIMENTAL RESULTS

## *A. System Configuration*

The systems used for the purpose of the experiments are dual-socket Intel-R Xeon-R CPU E5-2699 v4 (commonly labeled Broadwell cores) running at their maximum frequency of 2.2 GHz for all the cores. Intel-R Hyper-threading technology is turned on. Each system has 4 HFI(s) in each of the 4 x16 PCIe slots and Intel-R QuickPath Interconnect (QPI) links establish connection between the sockets. Two such servers are connected over a switch fabric using Omni-Path Edge switch.

|  | Algorithm 2 HFI selection algorithm for multi-rail |
| --- | --- |
|  | 1: procedure HFI MULTI-RAIL SELECTION |
| 2: | mrail MULT IRAIL ← envvarP SM2 |
| 3: | if mrail = 1 then |
| 4: | multirail setup across sockets() |
| 5: | return true |
| 6: | mrail else if = 2 then |
| 7: | activeunits ind available units() ← f |
| 8: | pnode node of current thread() ← numa |
| 9: | i < = 0;i availunits;i for + + do |
| 10: | hnode node of unit(i) ← numa |
| 11: | i if hf active(i) & hnode = pnode then |
| 12: | saved hf is[j++] ← i |
| 13: | end if |
| 14: | end for |
| 15: | multirail setup(saved hf is[]) |
| 16: | return true |
| 17: | elsereturn false |
| 18: | end if |
| 19: end procedure |  |

## *B. PSM2 Send and Receive*

A basic understanding of the PSM2 send and receive mechanism on Intel-R Omni-Path could aid in understanding the Experimental Results that are obtained.

- PSM2 contains two send mechanisms
- 1) Programmed I/O (PIO)
- 2) Send DMA (SDMA)

PIO send is optimized for low latency and message rate for smaller messages. Send DMA is optimized for high bandwidth and is used for larger messages. The decision to switch between the send mechanisms is based on a threshold message size set by the software (PSM2) and varies with different processor architectures.

PSM2 supports two receive mechanisms

- 1) Eager receive
- 2) Expected receive

The eager receive is intended for asynchronous receiving of packets by copying the received data to eager receive buffers. While the expected receive involves a handshake mechanism through which the send and receive sides are synchronized to transmit/receive packets through the HFI device. Expected receive supports direct data placement in application buffer.

In this paper we measure latency, message rate and bandwidth with the OSU micro-benchmarks (OMB) suite version 3.1.1 compiled using OpenMPI v1.10.4. Our evaluation is limited to synthetic benchmarks to be able to show clear performance benefits of affinity settings.

## *C. Bandwidth*

We measure bandwidth using osu bw and osu bibw from the OMB suite to show the benefit of our NUMA selection algorithm. We can see single HFI uni and bi-directional bandwidth performance for local and remote HFI in Figure 4 and Figure 5. Local HFI refer to the HFI connected to the same root complex, remote HFI refer to the HFI on the same server connected to the remote CPU socket that requires inter-socket communication over Intel-R QuickPath Interconnect (QPI). We see up to 40% better uni-directional bandwidth and up to 48% better bi-directional bandwidth by choosing the local HFI instead of the remote one. This performance difference is higher for small message sizes and hence our evaluation is focused on message size up to 8KB which are PIO send and eager receive. Further, all our measurements are consistent on both send and receive side to either use local HFI or remote HFI.

![](_page_4_Figure_1.png)

![](_page_4_Figure_2.png)

Fig. 4. OSU Bandwidth, Local vs Remote HFI with 1ppn

![](_page_4_Figure_4.png)

Fig. 5. OSU Bidirectional Bandwidth, Local vs Remote HFI with 1ppn

 

## *D. Latency*

Latency was measured using osu latency from the OMB suite. Figure 6 shows the difference in latency for different message sizes, worst case latency difference seen between local and remote HFI is up to 32%. The difference in latency is due to inter-socket communication overhead over QPI.

## *E. Message Rate*

Message rate was measured using osu mbw mr from OMB suite. Figure 7 shows message rate difference for varying message sizes from 1byte to 8KB. Peak message rate difference

![](_page_4_Figure_10.png)

Fig. 6. OSU Latency, Local vs Remote HFI with 1ppn

with one PPN(Process Per Node) is at about 40% between local and remote HFI.

![](_page_4_Figure_13.png)

Fig. 7. OSU Message Rate, Local vs Remote HFI with 1ppn

## *F. Multi-rail Use Case*

In our experiments with the multi-rail case where more than one HFI is used by MPI process(es), we see the benefits of the HFI device affinity scale for multiple HFIs. Figure 8 and 9 shows bandwidth differences between using two local HFIs which is the default case with our algorithm versus using two remote HFIs for one PPN(process per node)and two PPN case. Similar to the single HFI case, the dual HFI results shows significant performance difference until 8KB message size. Also it is clear from Figure 8 and Figure 9 that the multirail performance difference is in the same range as single HFI case for both one PPN and two PPN indicating the NUMA effects to scale with multiple HFI devices and impacts both single and multiple processes per node.

## IV. RELATED WORK

There has been a fair amount of research work done to analyze process placement and NUMA affinities with respect to different MPI applications. In [6], the authors explore cache effects, messaging and effects of process distribution

![](_page_5_Figure_0.png)

Fig. 8. OSU Bandwidth, Two local HFI affinity vs Using two remote HFI(s) with 1ppn

![](_page_5_Figure_2.png)

Fig. 9. OSU Bandwidth, Two local HFI affinity vs Using two remote HFI(s) with 2ppn

on MPI benchmarks. While they conclude that the effects of processor affinity were not as pronounced on certain workload characteristics, on some others there was clear application performance improvements due to correct processor affinity and NUMA placements. Chi et. al. [7] also study the effects of processor affinity but from the perspective of communication patterns within an application. From their experimental results it becomes evident that the impact of processor affinity depends heavily on the ratio of inter-node to intra-node communication patterns. However, the applications which were used for the experiments had more inter-node communication characteristics and the effect of processor affinity became almost negligible. Chai et. al. [3] study communication patterns with deeper analysis on the potential bottlenecks in multi-core clusters and how to avoid them. Their observation shows intra-socket communications shows best performance, but inter-socket does not perform well compared to inter-node due to cost of memory copies. Jeannot et. al. [4] present a TreeMatch algorithm that maps processes to computing resources based on a hierarchical arrangement of the elements in the system. They demonstrate the effects on performance of NAS benchmark and conclude that optimal process placement improves performance.

The topology mapping problem is NP-complete. Therefore, finding a near optimal solution through heuristic means is usually a more efficient approach. In this regard, a popular choice of algorithm seems to be the Dual Recursive Bipartitioning (DRB) method which uses a technique of graph mapping [8]. Mercier et. al. [9] use the SCOTCH [10] graph partitioning tool, which internally uses a DRB algorithm, to implement mapping of weighted cores in the system with MPI application. In [11], the authors also perform a comparative study of DRB with Maximum Weighted Perfect Matching (MWPM) approach which uses graph pairing with weights assigned for intra-chip, intra-node and then inter-node communication characteristics of the application. In general, the DRB algorithm seems to perform well for optimal placement of processes for a given MPI application. A common theme of above research works is to factor system architecture and application characteristics to model an optimal process placement solution. In [12], the researchers also factor in the network hierarchy and map the processes using an Isomorphic Tree mapping algorithm.

Realizing the increasing burden on application programmers to consider affinity issues during development due to increasing complexity of HPC systems, OpenMPI [13], using HWLOC [14] and Locality Aware Mapping Algorithm (LAMA) [15] introduced an interface for mapping the processes ranging from coarse-grained node level placement of the processes to fine-grained mapping onto hardware threads [16]. In cases where there are more than one IO device available on the node, a mapping pattern using "–map-by dist" option was provided for the user to choose a single device for the job [17]. This method requires application user to have knowledge of NUMA and to manually select a specific device for the job. Further, this method does not support multi-rail. However, this feature in OpenMPI has since been removed due to lack of support.

While previous research was focused on the effects of process placements relative to compute resources, our solution proposed here provides the best possible affinity between MPI process with respect to underlying communication devices.

## V. CONCLUSION AND FUTURE WORK

In this paper we introduce extensions to Intel-R Omni-Path MPI runtime layer, PSM2, by introducing environment variables for the application users to get optimal latency and bandwidth when multiple HFI devices are attached to the node. We also explain our NUMA aware network device selection algorithm in detail. Finally, we demonstrate performance benefits of NUMA aware IO device selection by comparing latency, bandwidth and message rate with OSU micro benchmarks [18].

As future work, the results presented in this paper provide insight into performance benefits of micro-benchmarks with optimal choice of network devices relative to MPI process placement, we like to extend this study to different class of HPC applications and publish comprehensive data.

Our primary focus here was intra-node processor to network device affinity. We would like to extend this to a combination of processor, memory and IO devices. Adding memory to the mix is important with the growing demand for hierarchical memory. While there is a need for sophisticated memory management to manage data stored in different memory types, it is important to keep the processor cores busy computing rather than waiting for IO operations. Achieving optimal network latency and bandwidth when the data is spread across different memory types is also an objective. For example, second generation Intel-R Xeon PhiTM processors contain limited amounts of on-package high bandwidth memory and relatively high capacities of DDR memory. Optimizing to maximize use of high bandwidth memory would be essential to keeping the processing cores busy and drive network traffic for certain classes of applications. Additions of non-volatile memory further increases the platform complexity requiring sophisticated NUMA aware software solutions.

## REFERENCES

- [1] "Non-unified memory access (NUMA)." [Online]. Available: https: //en.wikipedia.org/wiki/Non-uniform memory access
- [2] M. S. Birrittella, M. Debbage, R. Huggahalli, J. Kunz, T.Lovett, T. Rimmer, K. D. Underwood, and R. C. Zak, "Intel omni-path architecture: Enabling scalable, high performance fabrics," in *2015 IEEE 23rd Annual Symposium on High-Performance Interconnects*, Aug 2015, pp. 1–9.
- [3] L. Chai, Q. Gao, and D. K. Panda, "Understanding the impact of multicore architecture in cluster computing: A case study with intel dualcore system," in *Seventh IEEE International Symposium on Cluster Computing and the Grid (CCGrid '07)*, May 2007, pp. 471–478.
- [4] E. Jeannot and G. Mercier, "Near-optimal placement of mpi processes on hierarchical numa architectures," in *Proceedings of the 16th International Euro-Par Conference on Parallel Processing: Part II*, ser. Euro-Par'10. Berlin, Heidelberg: Springer-Verlag, 2010, pp. 199–210. [Online]. Available: http://dl.acm.org/citation.cfm?id=1885276.1885299
- [5] "PSM2." [Online]. Available: https://github.com/01org/opa-psm2
- [6] H. Pourreza and P. Graham, "On the programming impact of multicore,multi-processor nodes in mpi clusters," in *High Performance Com-*

*puting Systems and Applications, 2007. HPCS 2007. 21st International Symposium on*, May 2007, pp. 1–1.

- [7] C. Zhang, X. Yuan, and A. Srinivasan, "Processor affinity and mpi performance on smp-cmp clusters," in *2010 IEEE International Symposium on Parallel Distributed Processing, Workshops and Phd Forum (IPDPSW)*, April 2010, pp. 1–8.
- [8] E. R. Rodrigues, F. L. Madruga, P. O. A. Navaux, and J. Panetta, "Multicore aware process mapping and its impact on communication overhead of parallel applications," in *2009 IEEE Symposium on Computers and Communications*, July 2009, pp. 811–817.
- [9] G. Mercier and J. Clet-Ortega, "Towards an efficient process placement policy for mpi applications in multicore environments," in *Proceedings of the 16th European PVM/MPI Users' Group Meeting on Recent Advances in Parallel Virtual Machine and Message Passing Interface*. Berlin, Heidelberg: Springer-Verlag, 2009, pp. 104–115. [Online]. Available: http://dx.doi.org/10.1007/978-3-642-03770-2 17
- [10] F. Pellegrini, *Scotch and LibScotch 5.1 Users Guide*, INRIA Bordeaux-Sud-Ouest, ENSEIRB and LaBRI, UMR CNRS 5800, 2008.
- [11] M. K. Ferreira, V. S. Cruz, and P. O. A. Navaux, "Static process mapping heuristics evaluation for mpi processes in multi-core clusters," in *Latin American Conference on High Performance Computing (CLCAR)*, September 2011.
- [12] D. Li, Y. Wang, and W. Zhu, "Topology-aware process mapping on clusters featuring numa and hierarchical network," in *2013 IEEE 12th International Symposium on Parallel and Distributed Computing*, June 2013, pp. 74–81.
- [13] "Open MPI." [Online]. Available: https://www.open-mpi.org/
- [14] F. Broquedis, J. Clet-Ortega, S. Moreaud, N. Furmento, B. Goglin, G. Mercier, S. Thibault, and R. Namyst, "hwloc: A generic framework for managing hardware affinities in hpc applications," in *2010 18th Euromicro Conference on Parallel, Distributed and Network-based Processing*, Feb 2010, pp. 180–186.
- [15] J. Hursey, J. M. Squyres, and T. Dontje, "Locality-aware parallel process mapping for multi-core hpc systems," in *2011 IEEE International Conference on Cluster Computing*, Sept 2011, pp. 527–531.
- [16] J. Hursey and J. M. Squyres, "Advancing application process affinity experimentation: Open mpi's lama-based affinity interface," in *Proceedings of the 20th European MPI Users' Group Meeting*, ser. EuroMPI '13. New York, NY, USA: ACM, 2013, pp. 163–168.
- [17] "Process affinity: Hop on the bus gus." [Online]. Available: http://blogs.cisco.com/performance/process-affinity-hop-on-the-bus-gus
- [18] "OSU micro benchmarks." [Online]. Available: http://mvapich.cse. ohio-state.edu/benchmarks/

