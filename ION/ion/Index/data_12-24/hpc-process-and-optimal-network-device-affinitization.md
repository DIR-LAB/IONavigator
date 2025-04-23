# HPC Process and Optimal Network Device Affinitization

Ravindra Babu Ganapathi , Member, IEEE, Aravind Gopalakrishnan , Member, IEEE, and Russell W. McGuire, Member, IEEE

Abstract—High Performance Computing (HPC) applications have demanding need for hardware resources such as processor, memory, and storage. Applications in the area of Artificial Intelligence and Machine Learning are taking center stage in HPC, which is driving demand for increasing compute resources per node which in turn is pushing bandwidth requirement between the compute nodes. New system design paradigms exist where deploying a system with more than one high performance IO device per node provides benefits. The number of I/O devices connected to the HPC node can be increased with PCIe switches and hence some of the HPC nodes are designed to include PCIe switches to provide a large number of PCIe slots. With multiple IO devices per node, application programmers are forced to consider HPC process affinity to not only compute resources but extend this to include IO devices. Mapping of process to processor cores and the closest IO device(s) increases complexity due to three way mapping and varying HPC node architectures. While operating systems perform reasonable mapping of process to processor core(s), they lack the application developer's knowledge of process workflow and optimal IO resource allocation when more than one IO device is attached to the compute node. This paper is an extended version of our work published in [1]. Our previous work provided solution for IO device affinity choices by abstracting the device selection algorithm from HPC applications. In this paper, we extend the affinity solution to enable OpenFabric Interfaces (OFI) which is a generic HPC API designed as part of the OpenFabrics Alliance that enables wider HPC programming models and applications supported by various HPC fabric vendors. We present a solution for IO device affinity choices by abstracting the device selection algorithm from HPC applications. MPI continues to be the dominant programming model for HPC and hence we provide evaluation with MPI based micro benchmarks. Our solution is then extended to OpenFabric Interfaces which supports other HPC programming models such as SHMEM, GASNet, and UPC. We propose a solution to solve NUMA issues at the lower level of the software stack that forms the runtime for MPI and other programming models independent of HPC applications. Our experiments are conducted on a two node system where each node consists of two socket Intel Xeon servers, attached with up to four Intel Omni-Path fabric devices connected over PCIe. The performance benefits seen by applications by affinitizing processes with best possible network device is evident from the results where we notice up to 40 percent improvement in uni-directional bandwidth, 48 percent bi-directional bandwidth, 32 percent improvement in latency measurements, and up to 40 percent improvement in message rate with OSU benchmark suite. We also extend our evaluation to include OFI operations and an MPI benchmark used for Genome assembly. With OFI Remote Memory Access (RMA) operations we see a bandwidth improvement of 32 percent for fi_read and 22 percent with fi_write operations, and also latency improvement of 15 percent for fi_read and 14 percent for fi_write. K-mer MMatching Interface HASH benchmark shows an improvement of up to 25 percent while using local network device versus using a network device connected to remote Xeon socket.

Index Terms—Fabric, high performance computing, infiniband, MPI, NUMA, OFI, performance, process affinity, topology

Ç

### 1 INTRODUCTION

HPC applications place high demands on computation and requires fast networks to move data with low latency and high bandwidth across the nodes. HPC systems are built to run data-intensive modeling and simulation to solve a variety of scientific problems. More recently, HPC applications are developed to solve various Artificial Intelligence (AI) and Machine Learning (ML) problems. These applications work on large amount of data on the compute

For information on obtaining reprints of this article, please send e-mail to: reprints@ieee.org, and reference the Digital Object Identifier below. Digital Object Identifier no. 10.1109/TMSCS.2018.2871444

nodes and certain applications consists of data processing pipelines where the nodes process the data and transfer to adjacent node for the next stage of computation. This kind of pipeline processing on large data places high demand on the network device(s).

Department of Energy (DOE) published a report explaining the demand for data intensive sciences and exascale computing by 2020+ time frame [2]. This report also describes the challenges and gaps in technology and human skill set that needs to be addressed to satisfy future demands. One of the recommendation described in the DOE report was to improve the productivity of scientists involved in exascale and data intensive computing. Our solution described in this paper aims at moving large amount of data using multiple IO devices automatically with simple hints from the users. This will enable scientists and other domain experts to focus on the scientific problems and less on the implementation to move data efficiently across the network.

2332-7766 2018 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.

See http://www.ieee.org/publications_standards/publications/rights/index.html for more information.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

The authors are with the Intel Corporation, 2501 NE Century Blvd., Hillsboro, OR 97124. E-mail: {ravindra.babu.ganapathi, aravind.gopalakrishnan, russell.w.mcguire}@intel.com.

Manuscript received 12 Jan. 2018; revised 28 June 2018; accepted 4 Sept. 2018. Date of publication 20 Sept. 2018; date of current version 29 Jan. 2019. (Corresponding author: Aravind Gopalakrishnan.) Recommended for acceptance by R. Grant.

Intel provides two main processor solutions: Intel Xeon and Intel Xeon Phi processors which are intended for different audiences with diverse needs. Intel Xeon Phi processors have large number of small cores that are best suited for large massively parallel applications, and Intel Xeon processors have large powerful cores that provide limited parallelism but efficient in executing complex sequential code. While this provides good choices for different types of application developers, it further complicates platform architectures and necessitates application's affinity to processors and IO devices considering NUMA placement effects.

For HPC systems with fabric components, Intel Omni-Path Architecture (OPA) is designed to integrate seamlessly with CPU and memory components catering to the high performance metrics of low latency and high bandwidth. At the crux of OPA are Host Fabric Interfaces (HFI). HFIs connect each host to the fabric and act as the translation medium for host processor and fabric components. HFIs are concerned with implementing the physical and link layers of the fabric architecture such that the host can perform the basic send and receive functions with peers in the network. A more detailed overview of Intel OPA and hardware interfaces is conducted in [3].

IO devices, specifically network devices used in HPC clusters, are typically either Ethernet devices or low latency high bandwidth interconnect such as Intel Omni-Path devices or other Infiniband based devices. With the growing demand for higher I/O bandwidth in HPC clusters, systems can be configured with more than one network device per node.

In simple cases there is one network device per node connected over PCIe and all inter-node traffic goes over the single device. This gets cumbersome when more than one network device is attached to the node. These network devices can be either directly connected over PCIe or some of them can be connected over a PCIe switch.

Tokyo Tech's TSUBAME 3.0 [4], [5] super computer was ranked 1st on the Green500 list, announced at the International conference, ISC 2017 at Frankfurt, Germany. Each compute nodes of the TSUBAME 3.0 consists of several processing units along with four Intel Omni-Path devices to provide the high bandwidth and low latency communication between the nodes. This is a good example of next generation super computer requiring high data transfers between the nodes and hence using multiple IO devices per compute node.

On multi-socket node with multiple IO devices, one or more IO devices can be attached to each CPU socket. Process(es) running on a node communicating with process (es) on remote node(s) using a network device that is attached to the same CPU socket results in better performance than using an IO device that is attached to a different socket. The difference in performance is due to the additional inter-socket communication latency. In this paper we provide a detailed design and algorithms that can be implemented as part of PSM2 runtime to automatically choose the right IO device(s) for optimal performance, the benefits of which can be taken advantage of in other layers of middleware such as Libfabric and MPI. Further, we provide additional process configuration options to affinitize multiple IO devices to a process for cases where more than one IO device is needed for communication which is commonly termed as multi-rail.

This paper is an extended version of our work published in [1]. Our previous work was focused on verifying functional and performance claims by implementing affinity solution as part of Intel OPA software stack and measuring performance with standard OSU micro-benchmarks (OMB) benchmarks. In this paper we further extend the affinity solution to enable OpenFabric Interfaces (OFI) [6] which is generic HPC API that supports wider applications and is supported by various HPC fabrics as described in [7]. We also extend our evaluation on Intel Omni-Path fabric to include additional features provided by OFI such as Remote Memory Access(RMA) operations [8].

The rest of the paper is organized as follows. We explain design of HFI device affinitization in Section 2, which includes system configuration and provides device selection algorithms. Experimental results and the associated analysis for bandwidth, latency and message rate are provided in Section 3. Section 4 outlines related work and finally we conclude summarizing our findings and describing potential future work in Section 5

### 2 DESIGN OF HFI DEVICE AFFINITIZATION

#### 2.1 Design Motivation

The solution proposed in this paper aims at addressing the IO device affinity problem at the lowest level of the software stack. This approach enables middlewares such as MPI and PGAS languages build on top of the hardware specific low level software stack to benefit from the solution without explicit changes to each of the programming models. To satisfy this goal we implement our solution at the Performance Scaled Messaging (PSM2) [9] layer and evaluate the solution using OpenFabric Interface [6] and MPI benchmarks.

Performance Scaled Messaging [9] is the high performance scalable messaging library for Intel Omni-Path architecture that matches the semantics needed by MPI. Currently, PSM2 supports up to four HFI devices per node. Therefore, it includes some basic logic to identify available devices in the system and to find out which ones it can use for a given job. Open MPI and MVAPICH2 uses PSM2 as runtime for Intel Omni-Path devices.

OpenFabric Interface [6] is a high performance network API that was developed with deeper collaboration between industry and national labs as part of OpenFabric Alliance. OFIWG [7] or OpenFabric Interfaces working group is thriving to constantly enhance OFI to meet the demanding needs of the HPC community to support a generic API for HPC fabric. Middlewares enabled using OFI can seamlessly run on a variety of fabric devices. OFI currently supports several MPI and PGAS programming models that is listed on OFIWG [7] web page.

Libfabric is the library that is the core component of OFI that exports OFI API for applications and middleware libraries to use. Libfabric supports pluggable providers that hardware vendors can implement to enable OFI. PSM2 provider is part of libfabric that enables OFI over Intel Omni-Path devices. All our OFI evaluation in this paper is with OFI PSM2 provider. OFI through PSM2 provider expands PSM2 features to provide operations such as RMA operations [8]. OFI PSM2 Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

![](_page_2_Figure_1.png)

Fig. 1. Single HFI per node.

provider uses PSM2 API and hence our affinity solution implemented at the PSM2 layer is available with OFI. By evaluating with OFI, we prove that our affinity solution works with a wide variety of applications that are implemented with OFI over Intel Omni-Path devices.

#### 2.2 Node Configuration

In this paper, we propose solution to solve multi network device affinity issue to obtain optimal performance. All the experiments described in this paper are conducted with systems containing Intel Omni-Path devices. Further, each node is a dual socket Xeon server with two PCIe v3.0 slots with 16 lanes each. With this node configuration, we can have up to four Intel Omni-Path devices per node. The term Host Fabric Interface is also used to refer to Intel Omni-Path devices. Therefore, in this paper, we will be using the terms interchangeably.

Following are the three configurations in our experimental system requiring different affinity behavior:

- 1) Single HFI device per node
- 2) Two HFI devices per node, one per socket
- 3) Four HFI devices per node, two per socket

Configuration 1 shown in Fig. 1 is the simplest where all MPI traffic flows through the single device on the node.

Configuration 2 shown in Fig. 2 provides three different possible communication pattern for processes:

- 1) HFI device local to the socket
- 2) HFI device remote to the socket
- 3) Allow sending traffic over both HFI devices

Configuration 3 shown in Fig. 3 provides five different possible combinations of communication pattern for processes:

- 1) One HFI device local to the socket
- 2) One HFI device remote to the socket
- 3) Allow sending traffic over both HFI devices local to the socket
- 4) Allow sending traffic over both HFI devices remote to the socket
- 5) Allow sending traffic over all the devices in the system

Configuration 3's communication pattern is a super set of the above three configurations. Hence, our experiments are conducted on system with four Intel Omni-Path devices per node, each of these Intel Omni-Path devices connected to the same Intel Omni-Path Edge switch.

#### 2.3 HPC Process Affinity

With MPI predominantly being the programming model in use for HPC systems, we discuss some of the options available to us from MPI for addressing process and device affinity

![](_page_2_Figure_24.png)

Fig. 2. Dual HFI per node, one per socket.

problems. MPI process affinity depends on several factors. Using application inter-node and intra-node communications characteristics is a common heuristic. [10], [11]. To support user process placement strategies, MPI implementations usually provide their own run-time systems for launching and monitoring individual processes or use a back-end parallel run-time environment. Two widely used mapping patterns are "by-node" and "by-slot" methods. The "by-node" option allows users to place processes in a round-robin fashion among the nodes while "by-slot" performs a similar function among available "slots" (The definition of a slot could vary between different MPI implementations and platforms. Typically, it refers to processor cores or hardware threads). Modern resource managers carry support to allocate resources at core level while older systems provided only allocation support at node granularity.

MPI resource managers first allocate resources to a given MPI job. The mapping agent (provided by either resource manager or the MPI implementation) then creates a map of process to underlying processor cores and memory. This involves a specification of which processes is to be launched on each node and checks to prevent oversubscribing of any hardware resource. After mapping, each process is assigned a unique rank in MPI_COMM_WORLD. The ordering of ranks is important as it can map the ranks to resources in a round-robin (natural) format or a sequential format where first N ranks are placed on first node, second set of N ranks on second node and so on. At launch time, the runtime environment works with Operating System (OS) to bind the process to the cores determined from the earlier mapping and ordering phases.

For HPC workloads not using MPI as the underlying programming model, there may be other Operating system sprcific options to optimize process affinity. For example, Linux has taskset utility [12] to specify process affinity where as Microsoft Windows provides a command line option AFFINITY which accepts hexadecimal affinity masks. It may also be possible to assign affinity programatically using hwloc [13] (for Linux) or other OS specific solutions.

## 2.4 Device Selection Based on Process Affinity

## 2.4.1 PSM2 Environment Variables

PSM2 provides environment variables to control the behavior of affinity logic. A full description of PSM2 environment

![](_page_2_Figure_32.png)

Fig. 3. Four HFI devices per node, two per socket.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

variables is beyond the scope of this paper and hence we limit ourselves to describing relevant environment variables used. However, PSM2 source code has been open-sourced and is publicly available on GitHub [9].

- 1) PSM2_MULTIRAIL
- 2) PSM2_MULTIRAIL_MAP
- 3) HFI_SELECTION_ALG

PSM2_MULTIRAIL takes in values ranging from [0, 2]. The value of "0" is default behavior which is multi-rail switched off. A value of "1" tells PSM2 to use all available and active HFI(s) in the system for communication. A value of "2" instructs PSM2 to use multi-rail functionality but restrict the selection of HFI(s) to use within the NUMA node of currently running process. In this case, the NUMA node is the PCIe root complex of an Intel Xeon processor. For discussion in this paper, we enforce values of [1, 2] with this environment variable to compare performance with affinity logic or otherwise.

PSM2_MULTIRAIL_MAP accepts values in the form unit: port. This is input to PSM2 for selecting HFIs(unit) to use to set up the rails. If only one unit is specified, it is equivalent to a single-rail case. PSM2 parses the input to gather all units which serves as mask to limit multi-rail to the specified HFI(s). Unit values starts from 0 and Port value is always 1 indicating single port HFI. For purposes of experiments in the paper, we use this environment variable for evaluating worst case performance by listing HFIs from the remote socket.

HFI_SELECTION_ALG accepts arguments such as "Round Robin" and "Packed". Round Robin is the default mode where the job is evenly distributed across the HFI(s) available in the NUMA node. This is also the recommended mode of operation. The "Packed" mode allows user to completely subscribe the hardware contexts available from the first HFI device before moving to assign contexts in the next available HFI. If user prefers to spread job across all available HFI(s) in the system and not restrict to just the NUMA node (which is default), the user can override it by using "Round Robin All" as argument to the environment variable. For discussion in this paper, we allow default operation for this environment variable.

2.4.2 HFI Selection Algorithm PSM2 uses a combination of best fit and first fit approaches to select the HFI device to use for a particular process. After PSM2 scans the system looking for all available HFIs, it will first check if all available devices have the maximum number of free contexts. If this is the case, it likely means that no other job which uses PSM2 is running in the system. Therefore, PSM2 starts looking at the first available HFI in the system and tries to assign a context. If it fails for any reason, it tries next available HFI. In this manner, it keeps trying until one is assigned for current process. In the event that any HFI in the system is not idle, then its available contexts will be less than other HFIs. In this case, since PSM2 cannot reliably determine which HFI would have been chosen for an earlier job, it will try to spread the new job uniformly across all available HFIs in the system. Typically, this results in an uniform distribution of jobs across the HFIs. The user does have ability to manually choose the HFI to use for the job.

In this paper, we propose a modification to the existing default selection algorithm by taking into account the affinity of the processes. In the pseudo code (refer Algorithm 1), "hfival" represents the user provided input. If a value has been assigned by user (values greater than 0), we can return early and use the assigned HFI unit. Otherwise, the NUMA node affinity of all available HFIs in the system ("Hnode") is compared with the NUMA node affinity of the currently executing process ("Pnode"). If the values match, the HFI unit number is placed in a saved_hfis array. When there is only one HFI on the NUMA node local to the process, we can return the first item in the array. To ensure an uniform distribution of jobs across HFIs in case there are more than 1 HFI on the same local node, we invoke the spread_hfi function and return. If no HFIs are found on local NUMA node PSM2 will fall back to finding one on remote node.

Algorithm 1. HFI Selection Algorithm with Affinity Constrains

| 1: procedure HFI selection |  |
| --- | --- |
| 2: | chosen HFI or -1 hfival User |
| 3: | node of current pnode numa threadðÞ |
| 4: | > if hfival then return hfival ¼ 0 |
| 5: | else |
| 6: | active activeunits find unitsðÞ |
| 7: | if activeunits ¼ 1 then |
| 8: | hfival 0 return hfival |
| 9: | else |
| 10: | i < availunits;i for i ¼ 0; þ þ do |
| 11: | node of unit(i) hnode NUMA |
| 12: | if hfi & hnode activeðiÞ ¼ pnode then |
| 13: | saved hfis[j++] i |
| 14: | end if |
| 15: | end for |
| 16: | > 1 if j then |
| 17: | hfival spread hfiðsaved hfis½Þ |
| 18: | return hfival |
| 19: | else if j ¼ 1 then return saved_hfis [0] |
| 20: | else |
| 21: | remote node hfival select hfiðÞ |
| 22: | return hfival |
| 23: | end if |
| 24: | end if |
| 25: | end if |
| 26: end procedure |  |

2.4.3 Multirail Usage For systems where we have more than one HFI devices installed, MPI applications with more than one rank in the job per node will automatically leverage the available HFIs in the system. The user can provide hints to PSM2 using environment variables to help with choosing the correct HFI devices based on the core and NUMA socket on which the rank is placed by the job launcher.

Using the hints provided by the user application, PSM2 will attempt to find available and active HFIs within the same NUMA socket on which the MPI rank is launched. As shown in Algorithm 2, the logic is similar to the previous HFI selection algorithm. If user requests to use multirail across NUMA nodes ("mrail" value of 1), then we invoke the respective setup utility and return. Else, if request is for Multirail within a NUMA node ("mrail" value of 2), PSM2 will compare the NUMA node affinity of the currently Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

![](_page_4_Figure_1.png)

executing thread ("Pnode" value) with the NUMA node affinity of a list of HFIs obtained by probing the system ("Hnode" values). If matching values are found, then HFI unit numbers are added to a saved_hfis array. After system probing, each of the devices from the array is independently configured and context is assigned. Protocol level structures are duplicated for communication. With this algorithm, if PSM2 finds at least one HFI in the socket, it will choose to use it.

| Algorithm 2. | HFI Selection Algorithm for Multi-Rail |
| --- | --- |
|  | 1: procedure HFI multi-rail selection |
| 2: | MULTIRAIL mrail envvarPSM2 |
| 3: | if mrail ¼ 1 then |
| 4: | multirail setup across socketsðÞ |
| 5: | return true |
| 6: | else if mrail ¼ 2 then |
| 7: | available activeunits find unitsðÞ |
| 8: | node of current pnode numa threadðÞ |
| 9: | < availunits;i for i ¼ 0;i þ þ do |
| 10: | node of hnode numa unitðiÞ |
| 11: | & hnode if hfi activeðiÞ ¼ pnode then |
| 12: | saved hfis[j++] i |
| 13: | end if |
| 14: | end for |
| 15: | multirail setupðsaved hfis½Þ |
| 16: | return true |
| 17: | else return false |
| 18: | end if |
| 19: end procedure |  |

### 3 EXPERIMENTAL RESULTS

#### 3.1 System Configuration

The systems used for the purpose of the experiments are dual-socket Intel Xeon CPU E5-2699 v4 (commonly labeled Broadwell cores) running at their maximum frequency of 2.2 GHz for all the cores. Intel Hyper-threading technology is turned on. Each system has 4 HFI(s) in each of the 4 16 PCIe slots and Intel QuickPath Interconnect (QPI) links establish connection between the sockets. Two such servers are connected over a switch fabric using Omni-Path Edge switch.

#### 3.2 PSM2 Send and Receive

A basic understanding of the PSM2 send and receive mechanism on Intel Omni-Path could aid in understanding the Experimental Results that are obtained.

![](_page_4_Figure_10.png)

Fig. 4. OSU bandwidth, local versus remote HFI with 1 ppn. Fig. 5. OSU bidirectional bandwidth, local versus remote HFI with 1 ppn.

PSM2 contains two send mechanisms

- 1) Programmed I/O (PIO)
- 2) Send DMA (SDMA)

PIO send is optimized for low latency and message rate for smaller messages. Send DMA is optimized for high bandwidth and is used for larger messages. The decision to switch between the send mechanisms is based on a threshold message size set by the software (PSM2) and varies with different processor architectures.

PSM2 supports two receive mechanisms

- 1) Eager receive
- 2) Expected receive

The eager receive is intended for asynchronous receiving of packets by copying the received data to eager receive buffers. While the expected receive involves a handshake mechanism through which the send and receive sides are synchronized to transmit/receive packets through the HFI device. Expected receive supports direct data placement in application buffer.

In this paper we measure latency, message rate and bandwidth with the OSU micro-benchmarks suite version 3.1.1 compiled using Open MPI v1.10.4. We also use OFI applications and KMI HASH algorithm to showcase the performance benefits of affinity settings.

#### 3.3 Bandwidth

We measure bandwidth using osu_bw and osu_bibw from the OMB suite to show the benefit of our NUMA selection algorithm. We can see single HFI uni and bi-directional bandwidth performance for local and remote HFI in Figs. 4 and 5. Local HFI refer to the HFI connected to the same root complex, remote HFI refer to the HFI on the same server connected to the remote CPU socket that requires intersocket communication over Intel QuickPath Interconnect. We see up to 40 percent better uni-directional bandwidth and up to 48 percent better bi-directional bandwidth by choosing the local HFI instead of the remote one. This performance difference is higher for small message sizes and hence our evaluation is focused on message size up to 8 KB which are PIO send and eager receive. Further, all our measurements are consistent on both send and receive side to either use local HFI or remote HFI.

#### 3.4 Latency

Latency was measured using osu_latency from the OMB suite. Fig. 6 shows the difference in latency for different Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

![](_page_5_Figure_1.png)

Fig. 6. OSU latency, local versus remote HFI with 1 ppn.

![](_page_5_Figure_3.png)

Fig. 7. OSU message rate, local versus remote HFI with 1 ppn.

![](_page_5_Figure_5.png)

Fig. 8. RMA bandwidth for read operation, performance improvement of using local HFI versus remote HFI with 1 ppn.

message sizes, worst case latency difference seen between local and remote HFI is up to 32 percent. The difference in latency is due to inter-socket communication overhead over QPI. Note that for message sizes between 1 byte to 8 bytes, for the Local HFI case, the latency is less than 1us. This includes a switch hop and Packet Integrity Protection, a hardware error detection and correction mechanism which is always enabled.

#### 3.5 Message Rate

Message rate was measured using osu_mbw_mr from OMB suite. Fig. 7 shows message rate difference for varying message sizes from 1 B to 8 KB. Peak message rate difference with one Process Per Node (PPN) is at about 40 percent between local and remote HFI.

![](_page_5_Figure_10.png)

Fig. 9. RMA bandwidth for write operation, performance improvement of using local HFI versus remote HFI with 1 ppn.

![](_page_5_Figure_12.png)

Fig. 10. RMA latency for read operation, performance improvement of using local HFI versus remote HFI with 1 ppn.

#### 3.6 RMA Bandwidth

RMA Read and Write Bandwidth was measured using FI_READ and FI_WRITE operations with BANDWIDTH test type on OFI Ubertests [14]. Figs. 8 and 9 show the performance improvement in RMA bandwidth for different message sizes when using local HFI in comparison to the scenario when remote HFI was used. The bandwidth improvement between local and remote HFI for FI_READ is up to 32 percent. The bandwidth improvement for FI_WRITE operation up to 22 percent.

#### 3.7 RMA Latency

RMA Read and Write Latency was measured using FI_READ and FI_WRITE operations with LATENCY test type on OFI Ubertests. Figs. 10 and 11 show the performance improvement in RMA latency for different message sizes when using local HFI in comparison to the scenario when remote HFI was used. The latency improvement between local and remote HFI for FI_READ is up to 15 percent. The latency improvement for FI_WRITE operation up to 14 percent.

#### 3.8 Multi-Rail Use Case

In our experiments with the multi-rail case where more than one HFI is used by process(es), we see the benefits of the Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

![](_page_6_Figure_1.png)

Fig. 11. RMA latency for write operation, performance improvement of using local HFI versus remote HFI with 1 ppn.

![](_page_6_Figure_3.png)

Fig. 12. OSU bandwidth, two local HFI affinity versus using two remote HFI(s) with 1 ppn.

HFI device affinity scale for multiple HFIs. Figs. 12 and 13 shows bandwidth differences between using two local HFIs which is the default case with our algorithm versus using two remote HFIs for one process per node and two PPN case. Similar to the single HFI case, the dual HFI results shows significant performance difference until 8 KB message size. Also it is clear from Figs. 12 and 13 that the multirail performance difference is in the same range as single HFI case for both one PPN and two PPN indicating the NUMA effects to scale with multiple HFI devices and impacts both single and multiple processes per node.

#### 3.9 KMI HASH Benchmark

To demonstrate the performance of our solution with real world benchmark, we picked K-mer Matching Interface Hash [15] benchmark designed for distributed memory parallelism used for Genome assembly that is part of CORAL benchmark codes [16] intended for CORAL [17] systems. The query time and query throughput metrics reported by the BENCH_QUERY test of kmi-hash algorithm are of particular interest for our experiment as this portion of the workload contains much of the MPI communication. The total number of strings and the number of queries are two parameters that we vary to gather output from different problem sets. The relative performance improvement of the workload when using the local HFI is evident from the Fig. 14. For sake of brevity, x axis labels indicate the total number of queries/1e6. The total number of strings is an order of magnitude higher than the number of queries.

![](_page_6_Figure_8.png)

Fig. 13. OSU bandwidth, two local HFI affinity versus using two remote HFI(s) with 2 ppn.

![](_page_6_Figure_10.png)

Fig. 14. Query time for KMI Hash algorithm, performance improvement of using local HFI versus remote HFI with 1 ppn.

Depending on the problem set being used, we see up to 25 percent improvement when using the local HFI.

### 4 RELATED WORK

There has been a fair amount of research work done to analyze process placement and NUMA affinities with respect to different MPI applications. In [18], the authors explore cache effects, messaging and effects of process distribution on MPI benchmarks. While they conclude that the effects of processor affinity were not as pronounced on certain workload characteristics, on some others there was clear application performance improvements due to correct processor affinity and NUMA placements. Chi et al. [19] also study the effects of processor affinity but from the perspective of communication patterns within an application. From their experimental results it becomes evident that the impact of processor affinity depends heavily on the ratio of inter-node to intra-node communication patterns. However, the applications which were used for the experiments had more inter-node communication characteristics and the effect of processor affinity became almost negligible. Chai et al. [10] study communication patterns with deeper analysis on the potential bottlenecks in multi-core clusters and how to avoid them. Their observation shows intra-socket communications shows best performance, but inter-socket does not perform well compared to inter-node due to cost of memory copies. Jeannot et al. [11] presents a TreeMatch algorithm that maps processes to computing resources based on a hierarchical arrangement of the elements in the system. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

They demonstrate the effects on performance of NAS benchmark and conclude that optimal process placement improves performance.

The topology mapping problem is NP-complete. Therefore, finding a near optimal solution through heuristic means is usually a more efficient approach. In this regard, a popular choice of algorithm seems to be the Dual Recursive Bipartitioning (DRB) method which uses a technique of graph mapping [20]. Mercier et al. [21] use the SCOTCH [22] graph partitioning tool, which internally uses a DRB algorithm, to implement mapping of weighted cores in the system with MPI application. In [23], the authors also perform a comparative study of DRB with Maximum Weighted Perfect Matching (MWPM) approach which uses graph pairing with weights assigned for intra-chip, intra-node and then inter-node communication characteristics of the application. In general, the DRB algorithm seems to perform well for optimal placement of processes for a given MPI application. A common theme of the above research works is to factor system architecture and application characteristics to model an optimal process placement solution. In [24], the researchers also factor in the network hierarchy and map the processes using an Isomorphic Tree mapping algorithm.

Realizing the increasing burden on application programmers to consider affinity issues during development due to increasing complexity of HPC systems, Open MPI [25], using HWLOC [13] and Locality Aware Mapping Algorithm (LAMA) [26] introduced an interface for mapping the processes ranging from coarse-grained node level placement of the processes to fine-grained mapping onto hardware threads [27]. In cases where there are more than one IO device available on the node, a mapping pattern using "–map-by dist" option was provided for the user to choose a single device for the job [28]. This method requires an application user to have knowledge of NUMA and to manually select a specific device for the job. Further, this method does not support multi-rail. However, this feature in Open MPI has since been removed due to lack of support.

While previous research was focused on the effects of process placements relative to compute resources, our solution proposed here provides the best possible affinity between HPC process with respect to underlying communication devices.

### 5 CONCLUSION AND FUTURE WORK

This paper extends our previous work in [1] where we comprehensively describe the extensions to Intel Omni-Path MPI runtime layer, PSM2, by introducing environment variables for the application users to get optimal latency and bandwidth when multiple HFI devices are attached to the node. We also explain our NUMA aware network device selection algorithm in detail. Finally, we demonstrate performance benefits of NUMA aware IO device selection by comparing latency, bandwidth and message rate with OSU micro benchmarks [29].

In this paper we extend the affinity solution to Open-Fabric Interfaces [6] and demonstrate that the affinity solution seamlessly extends to OFI and hence expands to a large array of applications and middleware libraries [7]. provides performance benefit with OFI RMA operations [8] and KMI HASH [15] benchmark used for Genome assembly which was beyond the original intended purpose of our solution.

Our primary focus here was intra-node processor to network device affinity. We would like to extend this to a combination of processor, memory and IO devices. Adding memory to the mix is important with the growing demand for hierarchical memory. While there is a need for sophisticated memory management to manage data stored in different memory types, it is important to keep the processor cores busy computing rather than waiting for IO operations. Achieving optimal network latency and bandwidth when the data is spread across different memory types is also an objective. For example, second generation Intel Xeon Phi processors contain limited amounts of on-package high bandwidth memory and relatively high capacities of DDR memory. Optimizing to maximize use of high bandwidth memory would be essential to keeping the processing cores busy and drive network traffic for certain classes of applications. Additions of non-volatile memory further increases the platform complexity requiring sophisticated NUMA aware software solutions.

#### REFERENCES

- [1] R. B. Ganapathi, A. Gopalakrishnan, and R. W. McGuire, "MPI process and network device affinitization for optimal HPC application performance," in Proc. IEEE 25th Annu. Symp. High-Perform. Interconnects, Aug. 2017, pp. 80–86.
- [2] J. Chen, A. Choudhary, S. Feldman, B. Hendrickson, C. Johnson, R. Mount, V. Sarkar, V. White, and D. Williams, "Synergistic challenges in data-intensive science and exascale computing: DOE ASCAC data subcommittee report," Department of Energy Office of Science, Mar. 2013, https://www.scholars.northwestern.edu/ en/publications/synergistic-challenges-in-data-intensive-scienceand-exascale-com
- [3] M. S. Birrittella, M. Debbage, R. Huggahalli, J. Kunz, T. Lovett, T. Rimmer, K. D. Underwood, and R. C. Zak, "Intel omni-path architecture: Enabling scalable, high performance fabrics," in Proc. IEEE 23rd Annu. Symp. High-Perform. Interconnects, Aug. 2015, pp. 1–9.
- [4] Tokyo tech's tsubame 3.0. (Jun. 2017). [Online]. Available: https://www.titech.ac.jp/english/news/2017/038699.html
- [5] Japan keeps accelerating with Tsubame 3.0 AI supercomputer. (Feb. 2017). [Online]. Available: https://www.nextplatform.com/ 2017/02/17/japan-keeps-accelerating-tsubame-3–0-aisupercomputer/
- [6] P. Grun, S. Hefty, S. Sur, D. Goodell, R. D. Russell, H. Pritchard, and J. M. Squyres, "A brief introduction to the openfabrics interfaces - a new network API for maximizing high performance application efficiency," in Proc. IEEE 23rd Annu. Symp. High-Perform. Interconnects, 2015, pp. 34–39. [Online]. Available: http://dx.doi. org/10.1109/HOTI.2015.19
- [7] OpenFabric interfaces working group. [Online]. Available: https://ofiwg.github.io/libfabric/, Last Accessed: Sep. 2018.
- [8] OpenFabric interfaces RMA manual. [Online]. Available: https:// ofiwg.github.io/libfabric/master/man/fi_rma.3.html, Last Accessed: Jul. 2018.
- [9] PSM2. [Online]. Available: https://github.com/01org/opa-psm2, Last Accessed: Sep. 2018.
- [10] L. Chai, Q. Gao, and D. K. Panda, "Understanding the impact of multi-core architecture in cluster computing: A case study with intel dual-core system," in Proc. 7th IEEE Int. Symp. Cluster Comput. Grid, May 2007, pp. 471–478.
- [11] E. Jeannot and G. Mercier, "Near-optimal placement of MPI processes on hierarchical NUMA architectures," in Proc. 16th Int. Euro-Par Conf. Parallel Process.: Part II, 2010, pp. 199–210. [Online]. Available: http://dl.acm.org/citation.cfm?id=1885276.1885299
- [12] Taskset utility for Linux. [Online]. Available: https://linux.die. net/man/1/taskset, Last accessed: Apr. 2018.

Our benchmark results demonstrate that affinity solution Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:33:53 UTC from IEEE Xplore. Restrictions apply.

- [13] F. Broquedis, J. Clet-Ortega , S. Moreaud, N. Furmento, B. Goglin, G. Mercier, S. Thibault, and R. Namyst, "hwloc: A generic framework for managing hardware affinities in HPC applications," in Proc. 18th Euromicro Conf. Parallel Distrib. Netw.-Based Process., Feb. 2010, pp. 180–186.
- [14] OpenFabric interfaces fabtests repository. [Online]. Available: https://github.com/ofiwg/fabtests, Last accessed: Apr. 2018.
- [15] KMI HASH benchmark. [Online]. Available: https://asc.llnl.gov/ CORAL-benchmarks/Summaries/KMI_Summary_v1.1.pdf, Last Accessed: Jul. 2018.
- [16] Coral benchmark codes. [Online]. Available: https://asc.llnl.gov/ CORAL-benchmarks/, Last Accessed: Jul. 2018.
- [17] Coral. [Online]. Available: https://asc.llnl.gov/CORAL/, Last Accessed Jul. 2018.
- [18] H. Pourreza and P. Graham, "On the programming impact of multi-core,multi-processor nodes in MPI clusters," in Proc. 21st Int. Symp. High Perform. Comput. Syst. Appl., May 2007, pp. 1–1.
- [19] C. Zhang, X. Yuan, and A. Srinivasan,"Processor affinity and MPI performance on SMP-CMP clusters," in Proc. IEEE Int. Symp. Parallel Distrib. Process. Workshops PhD Forum, Apr. 2010, pp. 1–8.
- [20] E. R. Rodrigues, F. L. Madruga, P. O. A. Navaux, and J. Panetta, "Multi-core aware process mapping and its impact on communication overhead of parallel applications," in Proc. IEEE Symp. Comput. Commun., Jul. 2009, pp. 811–817.
- [21] G. Mercier and J. Clet-Ortega, "Towards an efficient process placement policy for MPI applications in multicore environments," in Proc. 16th Eur. PVM/MPI Users' Group Meet. Recent Advances Parallel Virtual Mach. Message Passing Interface, 2009, pp. 104–115. [Online]. Available: http://dx.doi.org/10.1007/978– 3-642-03770-2_17
- [22] F. Pellegrini, Scotch and LibScotch 5.1 User's Guide, INRIA Bordeaux-Sud-Ouest, ENSEIRB and LaBRI, UMR CNRS 5800, Aug. 2008, https://hal.archives-ouvertes.fr/hal-00410327.
- [23] M. K. Ferreira, V. S. Cruz, and P. O. A. Navaux, "Static process mapping heuristics evaluation for MPI processes in multi-core clusters," in Proc. Latin Amer. Conf. High Perform. Comput., Sep. 2011.
- [24] D. Li, Y. Wang, and W. Zhu, "Topology-aware process mapping on clusters featuring NUMA and hierarchical network," in Proc. IEEE 12th Int. Symp. Parallel Distrib. Comput., Jun. 2013, pp. 74–81.
- [25] Open MPI. [Online]. Available: https://www.open-mpi.org/, Last Accessed: Aug 2018.
- [26] J. Hursey, J. M. Squyres, and T. Dontje, "Locality-aware parallel process mapping for multi-core HPC systems," in Proc. IEEE Int. Conf. Cluster Comput., Sep. 2011, pp. 527–531.
- [27] J. Hursey and J. M. Squyres, "Advancing application process affinity experimentation: Open MPI's LAMA-based affinity interface," in Proc. 20th Eur. MPI Users' Group Meet., 2013, pp. 163–168.
- [28] Process affinity: Hop on the bus Gus. [Online]. Available: http:// blogs.cisco.com/performance/process-affinity-hop-on-the-busgus, Jan. 2014.
- [29] OSU micro benchmarks. [Online]. Available: http://mvapich.cse. ohio-state.edu/benchmarks/, Last Accessed: Sep. 2018.

![](_page_8_Picture_18.png)

Ravindra Babu Ganapathi received the MS degree in computer science from Columbia University, New York, in 2010. He is the technical lead/engineering manager responsible for technical leadership, vision, and execution of Intel OmniPath Libraries. In the past, he was the lead developer and architect for Intel Xeon Phi offload compiler runtime libraries (MYO, COI) and also made key contributions across Intel Xeon PHI software stack including first generation Linux driver development. Before Intel, he was lead

developer implementing high performance libraries for image and signal processing tuned for x86 architecture. His research interests spans across compilers, computer architecture, and high speed interconnects. He has published three research papers, holds a patent related to memory coherence: Method and system for maintaining release consistency in shared memory programming. He is a member of the IEEE.

![](_page_8_Picture_21.png)

Aravind Gopalakrishnan received the BTech degree in information technology from Anna University, Chennai, India, in 2010, and the MS degree in computer science from Ohio State University, Columbus, in 2012. Since graduation, he has worked with Advanced Micro Devices and Intel. His research interests include high performance computing systems, low latency, and high speed interconnects. He is a member of the IEEE.

![](_page_8_Picture_23.png)

Russell W. McGuire received the BS degrees in software engineering technology and computer engineering technology, in 2007. He has worked with Cadence Design Systems, International Business Machines, Software Technology Group, Universal Wide Band Technologies, Video Presence Inc, and Intel. His research topics include low latency, high speed networks, and secure low latency long-haul networks. He is a member of the IEEE.

" For more information on this or any other computing topic, please visit our Digital Library at www.computer.org/publications/dlib.

