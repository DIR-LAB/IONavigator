# Virtual I/O Caching: Dynamic Storage Cache Management For Concurrent Workloads

Michael Frasca Pennsylvania State University University Park, Pennsylvania mrf218@cse.psu.edu Ramya Prabhakar Pennsylvania State University University Park, Pennsylvania rap244@cse.psu.edu Padma Raghavan Pennsylvania State University University Park, Pennsylvania raghavan@cse.psu.edu Mahmut Kandemir Pennsylvania State University University Park, Pennsylvania kandemir@cse.psu.edu

## Abstract

A leading cause of reduced or unpredictable application performance in distributed systems is contention at the storage layer, where resources are multiplexed among many concurrent data intensive workloads. We target the shared storage cache, used to alleviate disk I/O bottlenecks, and propose a new caching paradigm to both improve performance and reduce memory requirements for HPC storage systems.

We present the virtual I/O cache, a dynamic scheme to manage a limited storage cache resource. Application behavior and the corresponding performance of a chosen replacement policy are observed at run time, and a mechanism is designed to mitigate suboptimal behavior and increase cache efficiency. We further use the virtual I/O cache to isolate concurrent workloads and globally manage physical resource allocation towards system level performance objectives.

We evaluate our scheme using twenty I/O intensive applications and benchmarks. Average hit rate gains over 17% were observed for isolated workloads, as well as cache size reductions near 80% for equivalent performance levels.

Our largest concurrent workload achieved hit rate gains over 23%, and an over 80% iso-performance cache reduction.

## 1. Introduction

Current system design trends employ resource consolidation, especially at the storage level, where disk resources are shared by numerous clients. This paradigm exists in leading supercomputers (e.g. Jaguar [1]), data centers, as well as cloud-computing clusters, such as Amazon's EC2 [2] or Microsoft's Azure platform [3]. This yields decreased system costs, simplified system management, and increased system utilization. An unfortunate side-effect is increased resource contention as independent applications with variable workloads compete for system resources. As a result, there is a Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. To copy otherwise, to republish, to post on servers or to redistribute to lists, requires prior specific permission and/or a fee.

SC11, November 12-18, 2011, Seattle, Washington, USA
Copyright 2011 ACM 978-1-4503-0771-0/11/11 ...$10.00.

clear need for effective and dynamic resource management.

We focus on the resource demands at the storage layer and develop a novel cache management strategy, the *virtual* I/O cache, to deliver increased hit rates and improved performance to client applications. This design is a response to recent application trends, where storage needs grow as ever larger datasets drive business and scientific requirements [4, 5]. In addition to performance issues, power requirements are a major concern and a clear barrier in the exascale roadmap [6]. Sophisticated storage nodes will support these massive systems, and their efficient design will be significant. Therefore, we also aim to reduce the required footprint of power-hungry DRAM.

In systems with concurrently-executing applications, effective storage cache management is a significant challenge due to application independence and dynamically changing resource demands. Recent studies address these issues with various caching techniques. Examples include: (i) adding new metrics for cache replacement policies such as frequency
[7], (ii) passing application hints that describe future accesses to the storage server [8], and (iii) identifying future data access patterns and prefetching blocks accordingly [9, 10]. These ideas focus on the data that applications use and estimate which data blocks should be cached to improve hit rates. In contrast, we offer a significantly new perspective that can be integrated with any of the existing approaches.

We focus on the application information gained from a chosen replacement policy and use this knowledge to manage storage caches at a higher level. For a given application, we determine I/O request features that cause the current replacement policy to perform sub-optimally and provide a compensation mechanism. This allows us to increase hit rates under a given cache budget, or dramatically reduce memory requirements and maintain high performance. Separately, we isolate I/O requests for each application and build an approach based on our intra-application data to achieve system-wide performance objectives.

The remainder of this paper is organized as follows. Section 2 clearly defines the use case and motivates the need for better cache management. Section 3 introduces the virtual I/O cache architecture. Section 4 describes our experimental platform and Section 5 presents our detailed evaluation of a virtual I/O cache under various workloads. Section 6 discusses related work and Section 7 concludes the paper.

## 2. **Motivation**

We examine the common scenario of a single storage node that is multiplexed among many independent applications.

The storage node consists of one or more disks that contain application data and a finite pool of physical memory that serves as a storage cache. Cache contents are intelligently managed to decrease average I/O latency and increase application performance. We find this setup as a generic component that many system implementations reflect.

Lustre, a high-performance distributed file system [11],
leverages this design paradigm. The disk subsystem consists of Object Storage Servers (OSS), which receive and handle I/O requests, and Object Storage Targets (OST),
which store data on persistent media [12]. An OSS manages multiple OST's, where each OST hosts up to 16 TB of data.

The Lustre file system supports many large scale supercomputing centers, such as the Oak Ridge National Laboratory
(ORNL), where it currently provides center-wide data access in the custom Spider file system [13, 14]. Spider supports over 26,000 clients and diverse workloads, as independent applications create and analyze massive data sets [15]. Our virtual I/O cache exploits workload diversity to satisfy high performance under constraints of limited cache space. This is relevant to the design of each OST, and can even support caching at the higher level of an OSS.

The DEMOTE policy [16], which cooperatively manages client and server caches, heavily influences our design. DEMOTE has a significant feature in which the client and server caches approximate a large unified LRU cache, e.g.,
exclusive caching is maintained, and data blocks leaving the tail of the client's LRU cache are demoted to the head of the server's LRU cache. The result is one large logical LRU cache that comprises two physical partitions. This design agrees with the LRU policy's basic assumptions, i.e., recency correlates with future access likelihood, and statically assigns the partition with greater recency to the low-latency client cache.

We recognize DEMOTE's static partitioning and introduce a novel generalization about this design point. It is not necessary to divide a unified logical cache into a fixed number of partitions, nor is it necessary to statically decide where each partition is located. The virtual I/O caching design will partition a large logical cache with greater flexibility than DEMOTE and is not specific to any one replacement policy. All replacement policies make *a priori* workload assumptions that are implied by their priority algorithms, and none is perfect for all applications. We show how to identify when a policy's assumptions are violated and create a novel mechanism to respond in these scenarios.

## 3. Virtual I/O Caching Framework

At its heart, the virtual I/O cache maintains 'ghost-caches' to achieve increased performance and isolation. A ghost cache, used by replacement policies such as 2Q and ARC [17, 18], maintains block identifiers (e.g. the page address) but does not include the actual page contents. This structure can track I/O request behavior beyond data currently within the physical storage cache. In our approach, ghost-caches will represent a unified caching construct in which logical caches are dynamically partitioned and partitions are dynamically assigned to physical memory. We term this instantiation as a *virtual I/O cache*.

![1_image_0.png](1_image_0.png)

![1_image_1.png](1_image_1.png)

Figure 1: Virtual I/O caching framework. (a) Single application: The VRM identifies the highly utilized cache regions, and the VPA maps these to the physical cache. (b) System level: Individual virtual caches are integrated with the G-VPA, which allocates physical space to each application. The proposed virtual I/O cache has three main components, the Virtual Resource Monitor (VRM), Virtual-Physical Allocator (VPA), and the Global Virtual-Physical Allocator
(G-VPA). We illustrate the application perspective in Figure 1 (a) and the system level view in (b). The VRM observes utilization of a large virtual cache and sends relevant data to the VPA. The VPA then generates a *mapping* that defines which virtual cache blocks should reside in the physical storage cache. Finally, the G-VPA is defined as a higherlevel unit to manage cache allocation among co-scheduled applications. There exists one virtual cache per application
(VRM+VPA), and it is the purpose of the G-VPA to determine how many cache blocks each application receives.

Virtual cache bookkeeping is done in parallel to physical cache accesses. Outstanding requests are satisfied as quickly as possible, since these immediately affect application performance, and the virtual bookkeeping is carried out in the background, i.e., it is not on the critical path. The VirtualPhysical Allocator runs periodically and modifies which virtual cache blocks are mapped to the physical resource.

Terminology. For clarity, we define our basic terminology. A *page* is an addressable region of disk (uniquely identified by its *page address*) that is referenced by an I/O request. Requested pages are brought into cache and placed in a *cache block*. The replacement policy approximates the utility of each page and decides which pages map to which cache block. In contrast, our virtual I/O caching mechanism will determine the utility of each cache block, and decide which cache blocks are assigned to the physical cache.

Replacement Queue. We generalize cache replacement policies as a priority queue, which we refer to as the *replacement queue*. A replacement policy maintains this queue based on various metrics such as recency and frequency [19, 20]. Using these metrics, the most valuable page is maintained at the head, and the least valuable is placed at the tail. The page at the tail will be targeted for eviction when a new page is brought into the cache. Most replacement algorithms are modeled by this abstraction, e.g., Least Recently Used (LRU) replacement pushes the most recently used (MRU) page to the head of the list and the keeps the least recently used page at the tail. We interchangeably refer to each *queue position* as a *cache block*. The replacement queue defines a logical view of the cache contents and may not correspond to actual data movement by the replacement policy. However, it is from this logical view that we identify the failures of a baseline policy.

## 3.1 Virtual Resource Monitor (Vrm)

We use the virtual cache to understand how a given workload is exploiting the features of a chosen replacement policy.

It is important to clearly state that we do not measure the utility of each page, as this is the purpose of the replacement algorithm. Instead, we are determining the utility of each cache block, i.e., each position in the replacement queue.

The main data structure of the VRM is the *virtual replacement queue*, which is a ghost-cache that functions as defined by the selected replacement policy and contains associated utility information. We measure utility based on access frequency in this design. At run time, we monitor each I/O reference and determine where the requested page is in the queue. A counter then measures the number of accesses to that cache position. Accordingly, our approach determines which cache positions are most utilized at run-time, while the baseline replacement policy simply assumes blocks at the head of the replacement queue have the highest access likelihood. If the application behaves as assumed by the replacement policy, we confirm this fact, and nothing is lost. If not, we now have the opportunity to fix the situation and cache the most relevant data. Utility data is periodically passed to the VPA (Section 3.2), which determines a new mapping of virtual cache blocks to the physical storage cache. This reclaims underutilized blocks from the physical cache and replaces them with valued blocks to improve the expected application hit rate, thereby reducing I/O latency.

We display a sample VRM value statistic in Figure 2. This information is a snapshot of an application utilizing a 256MB
virtual LRU cache. VRM data is aggregated per 1MB fragment of the virtual queue (discussed in Section 3.2). Lighter fragments have the highest access count. After some initial setup time, this code begins to frequently access pages in positions farther down the LRU queue. We also notice high variability between fragments, yet consistent behavior within a fragment. Consequently, we reason that intelligently staged data could satisfy most requests while requiring significantly less cache space.

History Decay. Mapping decisions are made periodically, and it is challenging to predict how long history infor-

![2_image_0.png](2_image_0.png)

Figure 2: VRM value data from the LU benchmark
(Section 4.1) utilizing an LRU replacement queue.

High utilization is found far from the queue's head. mation should be maintained before it no longer represents current cache use. Clearly, a balance must be struck between (a) keeping data long enough so that real trends are identifiable and (b) flushing stale history so that artifacts do not induce poor cache management decisions. We define a tuning parameter, α ∈ [0, 1], for this purpose. At the end of every time quantum, the value data at each position is multiplied by α to drive a geometric decrease in the relevance of previous quanta. In the case of the two extremes, only the most immediate access data is maintained when α = 0, and the entire application history is weighted equally if α = 1. Application specific knowledge can determine an optimal α choice, and we test sensitivity to this parameter in Section 5.3. This is similar to a mechanism in the LFUAging policy, where frequency data is periodically decayed by a factor two [21].

## 3.2 Virtual-Physical Allocator (Vpa)

The Virtual-Physical Allocator takes VRM utility data and intelligently decides which virtual queue positions should reside in the physical cache. We look back to Figure 2 and observe the high utilization of fragments between 128 and 192. Note that a traditional cache must be almost 192 MB
large to convert these requests into hits, but *this is not necessary when we exploit virtual I/O caching.* Assuming our virtual cache monitors a replacement queue that is large enough, the VPA can map regions of high utilization to a smaller physical cache. Computing the most effective physical mapping is non-trivial, and this work is our initial design. We present a simple mapping scheme in Algorithm 1 to motivate a discussion of various overheads. We assume a physical cache of size C blocks, and the VRM gives us an array *value* that describes the utility of position.

Overheads and Mitigation. The simple VPA algorithm maps the C most utilized queue positions to the physical cache, which reveals several issues that we address. We classify two types of overheads, (i) allocation overhead and
(ii) fragmentation overhead. *Allocation overhead* is incurred as data swaps into the physical cache during the re-allocation procedure. Fragmentation overhead is a more complicated metric, which we illustrate with an example.

Let us assume an LRU queue and a simple mapping for a 10 block physical cache. For a certain application, it was determined that LRU positions 0 through 4, and 10 through 14 are the most used. These 10 blocks are mapped to the physical cache, which creates 2 contiguous regions. We term these *fragments*. Essentially, there are two active partitions in which one serves the head of the LRU queue, and a second prefetches data as it enters positions 10-14.

VPA Mapping = { (0,1,2,3,4) ; (10,11,12,13,14) }
Algorithm 1 A simple VPA algorithm. Maps the C most valuable queue positions to the physical cache.

N = Virtual Cache Size (in blocks) C = Physical Cache Size (in blocks)
procedure CreateMapping(*value*)
map[i] = **false**, ∀ i ∈ [1, N]
for i ← 1, C do position = findMax(*value*) map[*position*] = **true**
value[*position*] = NULL
end for return map end procedure Consider an access to the page that position 4 contains.

This is a cache hit, and the page would move to the MRU
(position 0) as data in blocks 0 through 3 would shuffle down the queue. An access to position 5 generates a cache miss, which brings the requested page into the MRU position and pushes data in position 4 out to disk. More interesting behavior occurs when requests land in the second fragment, i.e., positions 10 through 14. Given an access to position 10, this page would move to the head, and the corresponding shuffle would push data at position 4 out of the physical cache as new data enters position 10. Although there was a cache hit, extra data movement occurs at fragment boundaries. Accesses beyond position 14 create transfers between cache and disk at positions 0, 4, 10, and 14. We call these extra transfers *fragmentation overhead*. We clarify that data does not physically move between cached fragments; this is a logical shuffling among cache blocks. Only on the fragment boundaries are physical data transfers required.

Extraneous data movement is easy to count, yet its impact is difficult to predict. These operations are not directly serving responses to the application but instead are actively managing the cache contents behind the scenes. Based on the implementation and current system load, these costs (or a portion of them) may be hidden to the application.

We apply two methods to reduce allocation and fragmentation overheads. First, we set a minimum size for all fragments. Typical file systems manage blocks at the granularity of 4KB pages [11, 22], but we keep track of VRM statistics at a coarser value (1MB, or 256 pages). This reduces allocation overhead, as variation within a fragment will not cause allocation changes. Second, we limit the total number of fragments allowed, which bounds fragmentation overhead.

This second parameter can be tuned based on the current demands at disk, and we study sensitivity to it in Section 5.3.

These constraints lead to a binpacking style problem solvable via a dynamic programming approach, but we instead develop a simple heuristic to minimize overheads. The initial pass computes a greedy mapping with Algorithm 1, then the current number of contiguous fragments is counted. While fragmentation is greater than the bound, the fragment with the least value is removed and then reallocated in a greedy fashion by adding blocks that neighbor the remaining fragments. Given these constraints, VRM value data is maintained at the granularity of a 1MB fragment and space overheads are limited to one scalar value per virtual cache MB.

Space overheads are therefore insignificant when compared to the underutilized cache that the virtual I/O may reclaim.

## 3.3 Global-Vpa: Concurrent Workloads

Concurrent workloads are easily supported by the virtual I/O caching framework. We present these details below, where all extensions are contained within one unit, the Global Virtual-Physical Allocator (G-VPA). The virtual cache components defined above maintain one replacement queue for a single application. When applications run concurrently, we generate a separate VRM and VPA for each application. Consequently, we have many virtual caches being observed, and the G-VPA manages how much physical resource is available to each, i.e., how many blocks are given to each application. This design was illustrated previously in Figure 1 (b).

We isolate virtual caches for several reasons. First, the VRM's main purpose is to observe the way in which an application distinctly utilizes the replacement queue. At run time, we can find that some portions of the queue are used far more often than others. If we model one queue for all applications, it is likely that interference will destroy the distinct individual patterns and exploitable trends will be lost.

Second, this gives a high quality mechanism to support different performance objectives. Each application has a VPA
which determines the best scheme for any given number of blocks. The G-VPA uses this information to determine the cache allocation that each application gets in accordance with the objective function. If bookkeeping overhead is too great, it is not required that each virtual cache is larger than the physical cache, but that the sum of all virtual caches is larger than the physical resource. Other motivations reflect the generality of the virtual I/O caching framework, e.g., each application can select its own replacement policy. Given application specific knowledge, the most effective replacement policy per application can be used in their respective VRMs, and optimal parameters (such as queue size and α, studied in Section 5.3) can be selected on a per application basis.

At the end of a time quantum, each VPA computes the best mapping for its current allocation. Furthermore, each computes the best mapping for a neighborhood of allocations, e.g., if an application currently owns k MB, the VPA
finds mappings for allocations of size k-1, k, and k+1 MB.

Each mapping has an associated value, e.g., the utilization of all cache blocks mapped, and this information is passed to the G-VPA. The G-VPA collects these data, makes an objective-maximizing allocation decision and then each virtual cache executes the appropriate mapping for its new allocation. We only evaluate the current neighborhood to minimize costs of the fragmented VPA algorithm and to manage allocation overhead between applications.

In this study, we target maximum aggregate system performance, which we define as the minimum number of cache misses across all applications. The best allocation is determined by comparing the marginal gain/loss of each mapping computed. An application gets an allocation increase if its marginal gain exceeds the loss incurred by the allocation decrease of another application.

## 3.4 Alternate Replacement Policies

In addition to LRU, we evaluate several notable replacement polices in the context of our design. We briefly introduce these well known approaches and describe their mapping to the virtual replacement queue.

LFU: The Least Frequently Used (LFU) policy prioritizes blocks by the number of accesses observed per page [20].

This cleanly maps to a priority queue, where pages are sorted by the access count. In our implementation, we use recency to break ties among pages with the same access count.

ARC: The Adaptive Replacement Cache (ARC) policy aims to automatically balance cache space between recency and frequency lists [18]. There are two LRU queues, where T1 contains all pages referenced once since they were last evicted, and T2, which contains pages that have been requested at least twice. Additionally, ARC has two ghost caches that keep track of evictions from T1 and T2. Requests that fall into these extensions help guide the target size of T1 vs. T2, and this target drives the eviction policy.

ARC's complex eviction policy leads to an incomplete mapping of each cache block to a global priority metric, and we thus choose one of many possible abstractions to a virtual replacement queue. We place T2 at the head of the replacement queue, and T1 starts after the T2's tail. This choice implies that all cache blocks in T2 are more valued than T1, though alternative mappings could interleave blocks from each queue. We choose this design, as we expect the virtual I/O cache will perform best when these two caches are separated, giving VRM that ability to independently monitor T1 and T2's run-time demand.

## 4. Experimental Setup

In this section, we describe the experimental setup used to measure the performance gains of the virtual I/O cache, as well as possible cache savings.

## 4.1 Application And Benchmark Traces

ORCA quantum chemistry suite. We use several components from the ORCA quantum chemistry package [23]
to evaluate our design. This package implements a diverse set of standard quantum chemical methods, with a focus on spectroscopic property calculations. We list trace descriptions in Table 1 and attributes in Table 2.

PDSI SciDAC. Sandia National Labs released sanitized I/O trace data from several application runs on Redstorm [24].

Each trace was collected at scale (6400 clients) running a light-weight operating system, Catamount [25]. These traces represent I/O requests from applications using Fortan I/O,
MPI-IO [26], and Parallel NetCDF [27] libraries. Additionally, Sandia released a trace from CTH, a three-dimensional shock physics application [28]. This trace comes from a run with 3300 clients. We convert these traces into block level serial traces and keep the first one million requests.

I/O benchmarks. We supplement our application traces with industry standard I/O benchmarks. From the NAS
parallel benchmarks, we use Block-Tridiagonal (BT) and LU-decomposition (LU) benchmarks [29]. For BT-IO, we use class sizes A, B, and C. Both the HP-IO benchmark [30]
and MPI Tile I/O benchmark [31] evaluate non-contiguous I/O performance for MPI-IO, and IOZONE is a general file system benchmark [32]. Finally, the TPC-C and TPC-R [33]
benchmarks represent transactional workloads for enterprise applications and web servers. Trace details are listed in Table 2 and are limited to the first one million requests.

## 4.2 Experimental Platform

We build our trace driven simulation platform to evaluate our design's performance. The ORCA and I/O benchmark traces are 4KB page references collected via *strace* [34] and

| Name   | ORCA Description                            |
|--------|---------------------------------------------|
| bsse   | Basis Set Superposition Error               |
| cass   | Complete Active Space Self-Consistent Field |
| cpf1   | Average Couple Pair Functional 1            |
| cpf2   | Average Couple Pair Functional 2            |
| dft1   | Density Functional Theory 1                 |
| dft2   | Density Functional Theory 2                 |
| uks    | Unrestricted Kohn-Sham                      |

| ORCA                 |                  |            |
|----------------------|------------------|------------|
| Name                 | Working Set (MB) | Length     |
| bsse                 | 12               | 69,149     |
| cass                 | 23               | 198,223    |
| cpf1                 | 13               | 345,747    |
| cpf2                 | 20               | 359,643    |
| dft1                 | 25               | 43,352     |
| dft2                 | 71               | 204,517    |
| uks                  | 21               | 79,648     |
| PDSI SciDAC          |                  |            |
| Name                 | Working Set (MB) | Length     |
| cth                  | 253              | 1,000,000+ |
| fortIO               | 713              | 1,000,000+ |
| mpiIO                | 356              | 1,000,000+ |
| pnetcdf              | 356              | 1,000,000+ |
| I/O Benchmark Traces |                  |            |
| Name                 | Working Set (MB) | Length     |
| btA                  | 400              | 307,409    |
| btB                  | 2,048            | 786,464    |
| btC                  | 1,619            | 1,000,000+ |
| hpio                 | 1,537            | 789,708    |
| iozone               | 288              | 1,000,000+ |
| lu                   | 526              | 1,000,000+ |
| mpitile              | 255              | 1,000,000+ |
| tpcc                 | 276              | 938,043    |
| tpcr                 | 620              | 1,000,000+ |

serve as input to our cache simulator. The VRM component monitors replacement queue statistics on-line, and the VPA is invoked periodically to change the virtual-physical cache mapping. Traces were collected on multiple platforms and timing aspects of the trace cannot be accurately reconstructed for our concurrent experiments. Therefore, we simplify the simulator's timing model to clearly isolate the effects of virtual caching. We execute these traces in a lockstep, round-robin fashion. The virtual I/O cache provides a powerful generalization of cache replacement policies, and therefore defines a significant parameter space. We include a sensitivity analysis with respect to fragment bound (f), history decay (α), and time quantum (q). From this analysis, we choose a reasonable parameter set for the main experiments (f = 2, α = 0.95, q = 2000).

5. RESULTS
We simulate a virtual I/O cache running multiple replacement policies and evaluate its performance for isolated and concurrent workloads. We also conduct a sensitivity study with respect to our design parameters.

![5_image_0.png](5_image_0.png) 

## 5.1 Single Workload Results

We begin our virtual caching evaluation with applications running in isolation and consider a 1GB virtual cache. We evaluate LRU, LFU, and ARC policies and observe physical cache sizes that range from 2MB to 1GB. In the top row of Figure 3 (a), we present average hit rates across all 20 benchmarks and include 95% confidence intervals. We see a clear advantage of the virtual I/O cache over the traditional LRU, which is most significant at small physical cache sizes.

Similar behavior is observed with LFU and ARC replacement policies in Figure 3 (b) and (c). These data show that VRM can identify the suboptimal priority decisions for each replacement policy. For the LRU policy, the average hit rate improvement is 17.32% for cache sizes from 32 MB to 256 MB. LFU and ARC see average gains of 16.76% and 11.01% over the same range, respectively. Gains are least with the ARC policy, which is likely due to the ill-specified mapping to a logical priority queue.

As shown, our cache management strategy generates significant performance gains on average. The virtual I/O
cache's capability is even more striking when we look at the inverse problem. Traditional replacement policy works aim to increase hit rates for a given cache budget. The virtual I/O cache identifies poorly utilized blocks, and can therefore maintain high performance with a drastically reduced cache budget. Minimizing DRAM requirements is crucial towards exascale computing goals, as a significant portion of system power is consumed by DRAM [6]. In second row of Figure 3, we observe the possible savings in required cache size when we target a specified average hit rate. Between the range of 60 - 80% target hit rates, average cache savings is 92.74%,
66.37%, and 72.65% for LRU, LFU, and ARC. When running a 1GB virtual LRU cache, our scheme achieves a target hit rate of 80% using only 160MB of cache (a savings of 79.17% over the baseline 768 MB required).

We gain additional insight as we look at cache behavior per application. For about half of our benchmarks, we saw no improvement at all. There are two possible reasons for this: (i) the application is cache insensitive (e.g. streaming accesses), or (ii) it effectively utilizes the replacement policy.

The first issue is a target for cache prefetchers and orthogonal to our work. In the second, these applications' behavior agrees with LRU assumptions and fragments selected by the VPA are usually at the head of the replacement queue. In either case, the virtual cache still collects useful application information and will enable effective management decisions in a co-scheduled environment. With respect to LRU,
benchmarks hpio, btB, and btC were found to have significant streaming behavior, while bsse, cpf1, cpf2, uks, and tpcr performed well with the baseline policy.

In Figure 4, we present the applications that benefit from the LRU virtual cache across several cache sizes. We also include the maximum hit rate achieved at a 1GB physical cache, to put these data into perspective. These gains are striking, as several benchmarks nearly achieve a maximum hit rate with only 16MB cache. As physical cache size grows to cover the working set of smaller applications, we see fewer benchmarks with gains, though still massive gains where opportunity remains.

We further examine cache profiles for several benchmarks in Figure 5. We see that MPI Tile uses the LRU queue with near zero efficiency until the cache reaches 256 MB. This is induced by a looping access pattern, which can be easily identified by a prefetching algorithm, yet we see the simple design of the virtual I/O cache equally exploits this behavior.

PnetCDF has more interesting behavior, were many accesses

![6_image_0.png](6_image_0.png) 

Figure 4: Hit rate gains per application, comparisons against 16, 32, and 64MB LRU caches. For these applications, the virtual cache enables dramatic gains. Maximum achievable hit rate (1GB physical cache) is added for reference.

![6_image_1.png](6_image_1.png) 

are spread between LRU queue positions 256 - 512MB. We learn this behavior and use the limited cache space to achieve high gains from 2 - 256 MB. After 512 MB, the baseline scheme naturally catches up. We also present two less advantageous scenarios with LU and TPCC.

## 5.2 Concurrent Workload Results

Based on the isolated experiments, we have found that some applications benefit from a virtual I/O cache much more than others. Although some did not benefit in an isolated sense, we expect system wide improvements in a co-scheduled environment as the G-VPA will ensure that these cache insensitive applications do not grab more physical blocks than necessary. We measure performance of four separate workloads, listed in Table 3. The first (W4) is a set of ORCA applications with relatively small total working set. We increase memory pressure in W8 by adding PDSI
applications, and further stress the system with more ORCA
applications and I/O benchmarks in W16. Finally we test full concurrency with all applications in workload W20.

Our virtual cache parameters are the same as the single workloads experiments above (f = 2, α = 0.95, q = 2000).

We simulate physical caches up to 1GB, and equally partition cache space at the start of the run. There is one 1GB
VRM+VPA per application, and at the end of each time quantum, each VPA computes mappings for current and neighboring allocations, and the global VPA selects the combination that maximizes total cache value (see Section 3.3).

Overall system performance, in terms of storage cache hit rate, is presented in the top row of Figure 6. For each workload, significant gains are seen at smaller cache sizes, and the benefits diminish as the physical cache grows to contain the entire active working set. The largest absolute gains exist under W4 and W8 workloads and cache sizes below 64MB,
yet there are still significant gains for the largest workloads.

| Name   | Description                                                   |
|--------|---------------------------------------------------------------|
| W4     | cass, dft1, dft2, uks                                         |
| W8     | {W4} + cth, fortIO, mpiIO, pnetCDF                            |
| W16    | {W8} + bsse, cpf1, cpf2, mr2, btA, + lu, hpio, iozon, mpitile |
| W20    | All Benchmarks                                                |

W16 achieves a 30.4% absolute gain at 128MB, and W20 achieves a 23.97% gain at 120MB.

As stated in Section 3.2, there are two sources of overhead, which we measure as the number of extra data transfers between the cache and disk. The virtual I/O scheme uses run-time data to gain valuable application insight and acts upon this information to intelligently stage data in cache.

Allocation overhead occurs at the end of a quantum, as a new mapping swaps blocks into the physical cache. Fragmentation overhead results from extra data movement at fragment boundaries. The bottom row of Figure 6 presents these overheads relative to the number of I/O requests. We stack these data, with direct misses first, followed by allocation overhead and then fragmentation overhead. Allocation overhead adds relatively few extra disk transfers in all cases, while most overhead is incurred due to fragmentation. Above the minimum cache sizes, total disk activity is greater than the baseline scheme, and this increased traffic is exploited to increase storage cache hit rates. We see a 0.33 gain in disk activity per request for W16 at 128 MB,
which we noted led to a 30.4% hit rate increase. For W20, a hit rate gain of 23.97% at 120 MB was supported by an 0.11 gain in disk I/O per request.

Finally, we present cache saving opportunities in Figure 7.

Assuming the target hit rate is within the reach of the baseline policy, we again see incredible savings in cache re-

![7_image_0.png](7_image_0.png) 
quirements. Maximum baseline hit rates for W16 and W20 are 80.04% and 69.82% respectively, and these targets are reached via our scheme at 384 MB for W16 and 180 MB for W20. These translate into 62.5% and 82.4% cache reductions over a 1GB physical cache.

## 5.3 Sensitivity Study

Our virtual I/O cache design has introduced several tuning parameters: history decay (α), time quantum (q), and fragment count (f). Each application can have its own optimal values, but we conduct a sensitivity analysis to discover general trends. For a range of parameters, we simulate each workload and monitor system hit rates and overheads. Three experiments are run, and we vary each parameter independently from the standard setup in Section 5.1
(i.e. f = 2, α = 0.95, q = 2000). It is important to note there is interaction between q and α, as history decay is a function of both, and they should be optimized concurrently.

Average hit rates are shown in Figures 8 (a), (b), and
(c) for each tuning. We expect allocation overhead to depend on q and α. The VPA is invoked less often for larger quanta, generating fewer re-allocations. When α is near 1, historic data decays slowly and the VRM data is more stable. This should also reduce allocation overheads. Our expectations are confirmed in Figures 8 (d) and (e), which presents overheads relative to the baseline. Unfortunately, the relationship between these parameters and overall hit rate is conflicting and a balance must be sought. At run time, we suggest a feedback mechanism that tunes q and α based on disk utilization, and plan to study this with future work.

In Figures 8 (c) and (f), we measure the impact of fragment count. As f increases, the VPA has greater mapping flexibility and disparate locations in the replacement queue can be staged. This naturally increases hit rates, but we find that fragmentation overhead grows quickly. We see f = 2 as a good balance, which is confirmed by our main experimental section.

We estimate the impact of fragmentation and reallocation overheads for isolated workloads by implementing a simple disk model with constant access latency and measuring disk utilization. Overhead disk transfers are queued at the disk and subsequent application I/O requests are delayed until all outstanding disk events are processed. We choose MPI
Tile and LU benchmarks and use the same setup in Section 5.1. We simulate a 32 MB physical cache and measure disk utilization as simulated disk latency varies. The data in Figure 9 show that utilization impacts are not significant for these workloads, and the massive gains in cache hit rates are easily achieved without inducing disk bottlenecks. We plan future work to measure overheads in a concurrent setting and provide feedback mechanisms that tune cache parameters when overheads interfere with application performance.

## 6. Related Work

Various optimizations for improving the I/O performance have been proposed in the literature, which we categorize as prefetching policies, replacement policies, and allocation policies. Many prefetching designs have emerged to hide I/O latencies [35, 36, 9, 10]. Our work is orthogonal to prefetching but can be used alongside such techniques. Since the VRM monitors the value of cache blocks, any integration could effectively allocate resources between storage cache and prefetching space.

Similarly, our virtual I/O cache is independent of existing replacement policy works. The well-known replacement algorithms of LRU [19] and LFU [20] measure recency and frequency of page requests to determine which data should be replaced. Several variants such as 2Q [17] and MultiQ [37]
algorithms identify blocks with different access frequencies using two or multiple LRU queues, respectively. In LRU-

![8_image_0.png](8_image_0.png) 

![8_image_1.png](8_image_1.png) 
k [38], pages are prioritized by their backward K-distance.

Similarly, LRFU [7], LIRS [39], ARC [18], and CAR [40] use variations in LRU and LFU replacement policies to prioritize blocks for eviction. All of these works can be generalized to different implementations of a replacement queue, where each defines its metrics and policy to prioritize requested data pages. We provide a distinct contribution to storage cache management, as our approach uses run-time information to determine suboptimal priority decisions from the current replacement policy. Regardless of the chosen policy, we evaluate cache blocks, not data pages, and ensure that the most demanded blocks reside in the physical storage cache. Furthermore, related replacement policy works increase the value of our virtual I/O cache design, as the best replacement policy can be selected on a per application basis. On-line policy analysis was shown to work in [41], which also introduces a technique of background rollover that reduces costs when switching between replacement policies.

This idea could be applied during reallocation, though we observed allocation overheads to be small in our study.

We supplement related works on storage cache allocation, which are designed to minimize interference at the storage layer. Cache interference leads to significant performance degradation and reduces overall system throughput. To alleviate this problem, many researchers have explored cache partitioning designs that attempt to avoid conflicts among multiple applications [42, 43, 44, 45, 46]. Shared storage cache space has also been partitioned based on the access patterns of multiple processes [47, 48]. In our work, we show that dynamic cache allocation is a simple yet effective capability when built upon individual virtual I/O caches.

The G-VPA design leverages the VRM utility measurements needed by the VPA, thus adding little overhead. It is also flexible in terms of the system performance objective.

## 7. Conclusions And Future Work

In this paper, we have introduced virtual I/O caching as a new paradigm for managing shared storage caches. We designed this framework as a general tool that can be purposed for any workload mix. Given relevant application knowledge, an implementation can choose the best cache replacement policy and VRM/VPA parameters on a per application basis, and effective cache management decisions can be made regardless of each application's isolated behavior. We presented simulation results for multiple baseline replacement policies under single workload conditions, and studied system performance under scenarios of twenty concurrent workloads. The virtual I/O cache ensures that physical storage cache is partitioned between applications to achieve increased system performance, and that each application uses its allocation in a way that avoids caching under-utilized blocks.

This work can be extended to several possible directions.

We plan to study more objective functions, e.g., application fair speedup and QoS metrics, and design VPA components that achieve these objectives. We would also like to support the virtual I/O cache framework with feedback mechanisms that automatically tune VRM parameters. Finally, we see a need to extend the concept of virtual I/O caching to systems with distributed storage nodes and therefore, distributed storage caches.

In summary, we have proposed the virtual I/O cache framework and provided simulation results to support its efficacy.

We evaluated concurrent workloads over a large range of cache sizes and experimented with twenty I/O intensive scientific applications and benchmarks. We observed average hit rate gains over 17% in the single workload case or cache size reductions near 80% for equivalent performance levels. Our largest concurrent workload achieved hit rate gains over 23%, and achieved an over 80% iso-performance cache reduction.

## 8. References

[1] A. Bland, R. Kendall, D. Kothe, J. Rogers, and G. Shipman, "Jaguar: The World's Most Powerful Computer," 2009.

[2] "Amazon elastic compute cloud,"
http://aws.amazon.com/ec2.

[3] D. Chappell, "Introducing windows azure," *Microsoft,*
Dec, 2009.

[4] J. M.-C. et al., "Software for leadership-class computing," *SciDAC Review*, 2007.

![9_image_0.png](9_image_0.png) 
[5] D. Howe, M. Costanzo, P. Fey, T. Gojobori, L. Hannick, W. Hide, D. Hill, R. Kania, M. Schaeffer, S. St Pierre *et al.*, "Big data: The future of biocuration," *Nature*, vol. 455, no. 7209, pp. 47–50, 2008.

[6] J. Shalf, S. Dosanjh, and J. Morrison, "Exascale Computing Technology Challenges," High Performance Computing for Computational Science–VECPAR 2010, pp. 1–25, 2011.

[7] Donghee Lee et al., "On the existence of a spectrum of policies that subsumes the least recently used (LRU)
and least frequently used (LFU) policies," in SIGMETRICS, 1999.

[8] G. Yadgar, M. Factor, and A. Schuster, "Karma:
Know-it-all replacement for a multilevel cache," in FAST, 2007.

[9] C. Li, K. Shen, and A. Papathanasiou, "Competitive prefetching for concurrent sequential I/O," ACM
SIGOPS Operating Systems Review, vol. 41, no. 3, p.

202, 2007.

[10] B. Gill and D. Modha, "SARC: Sequential prefetching in adaptive replacement cache," in Proceedings of the annual conference on USENIX Annual Technical Conference. USENIX Association, 2005, p. 33.

[11] P. Schwan, "Lustre: Building a file system for 1000-node clusters," in Proceedings of the 2003 Linux Symposium. Citeseer, 2003.

[12] "Lustre File System,"
http://wiki.lustre.org/manual/LustreManual18 *HTML/*.

[13] W. Yu, J. Vetter, R. Canon, and S. Jiang, "Exploiting Lustre File Joining for Effective Collective IO," in Proceedings of the Seventh IEEE International Symposium on Cluster Computing and the Grid. IEEE Computer Society, 2007, pp. 267–274.

[14] G. Shipman, D. Dillow, S. Oral, and F. Wang, "The spider center wide file system: From concept to reality," in Proceedings, Cray User Group (CUG)
Conference, Atlanta, GA, 2009.

[15] G. Shipman, D. Dillow, S. Oral, F. Wang, D. Fuller, J. Hill, and Z. Zhang, "Lessons Learned in Deploying the World's Largest Scale Lustre File System," in The 52nd Cray User Group Conference, 2010.

[16] T. M. Wong and J. Wilkes, "My cache or yours?

making storage more exclusive," in *USENIX Annual* Technical Conference, General Track, 2002, pp.

161–175.

[17] T. Johnson and D. Shasha, "2Q: A low overhead high performance buffer management replacement algorithm," in *VLDB*, 1994.

[18] N. Megiddo and D. Modha, "ARC: A self-tuning low overhead replacement cache," in *FAST*, 2003.

[19] A. Silberschatz, P. Galvin, G. Gagne, and A. Silberschatz, *Operating system concepts*. Addison-Wesley New York, 1994, vol. 89.

[20] J. Robinson and M. Devarakonda, "Data cache management using frequency-based replacement," in SIGMETRICS, 1990.

[21] ——, "Data cache management using frequency-based replacement," *ACM SIGMETRICS Performance* Evaluation Review, vol. 18, no. 1, pp. 134–142, 1990.

[22] W. Yu, J. Vetter, and H. Oral, "Performance characterization and optimization of parallel I/O on the Cray XT," in Parallel and Distributed Processing, 2008. IPDPS 2008. IEEE International Symposium on. IEEE, 2008, pp. 1–11.

[23] F. Neese, "ORCA-an ab initio," *Density Functional* and Semiempirical Program Package, Version, vol. 2, 2004.

[24] L. Ward, "PDSI SciDAC: Released Trace Data,"
www.cs.sandia.gov/Scalable IO/SNL Trace *Data/*.

[25] S. Kelly and R. Brightwell, "Software architecture of the light weight kernel, Catamount," in *Proceedings of* the 2005 Cray User Group Annual Technical Conference, 2005.

[26] P. Corbett, D. Feitelson, S. Fineberg, Y. Hsu, B. Nitzberg, J. Prost, M. SNiRf, B. Traversat, and P. Wong, "Overview of the MPI-IO Parallel I/O
Interface," High performance mass storage and parallel I/O: technologies and applications, p. 477, 2002.

[27] J. Li, W. Liao, A. Choudhary, R. Ross, R. Thakur, W. Gropp, R. Latham, A. Siegel, B. Gallagher, and M. Zingale, "Parallel netCDF: A high-performance scientific I/O interface," in *Proceedings of the 2003* ACM/IEEE conference on Supercomputing. IEEE
Computer Society, 2003, p. 39.

[28] E. Hertel Jr, R. Bell, M. Elrick, A. Farnsworth, G. Kerley, J. McGlaun, S. Petney, S. Silling, P. Taylor, and L. Yarrington, "CTH: A software family for multi-dimensional shock physics analysis," in in Proceedings of the 19th International Symposium on Shock Waves, held at. Citeseer, 1993.

[29] P. Wong et al., "NAS parallel benchmarks I/O version 2.4." in Technical Report NAS-03-002, Computer Sciences Corporation, NASA Advanced Supercomputing (NAS) Division, NASA Ames Research Center, 2003.

[30] A. Ching et al., "Evaluating I/O characteristics and methods for storing structured scientific data," in IPDPS, 2006.

[31] R. Ross, "Parallel I/O benchmarking consortium,"
2005.

[32] D. Capps and W. Norcott, "IOzone filesystem benchmark," 2008.

[33] M. Poess and C. Floyd, "New TPC benchmarks for decision support and web commerce," *ACM Sigmod* Record, vol. 29, no. 4, pp. 64–71, 2000.

[34] R. McGrath and W. Akkerman, "Source Forge Strace Project."
[35] S. Vanderwiel and D. Lilja, "Data prefetch mechanisms," *ACM Computing Surveys (CSUR)*,
vol. 32, no. 2, pp. 174–199, 2000.

[36] D. Callahan, K. Kennedy, and A. Porterfield,
"Software prefetching," ACM SIGARCH Computer Architecture News, vol. 19, no. 2, p. 52, 1991.

[37] Y. Zhou and J. F. Philbin, "The multi-queue replacement algorithm for second level buffer caches," in *USENIX*, 2001.

[38] E. J. O'Neil, P. E. O'Neil, and G. Weikum, "The lru-k page replacement algorithm for disk buffering," in ACM SIGMOD International Conference on Management of Data, 1993.

[39] S. Jiang and X. Zhang, "LIRS: An efficient low interreference recency set replacement policy to improve buffer cache performance," in *SIGMETRICS*,
2002.

[40] S. Bansal and D. Modha, "CAR: Clock with adaptive replacement," in *FAST*, 2004.

[41] R. Gramacy, M. Warmuth, S. Brandt, I. Ari *et al.*,
"Adaptive caching by refetching," Advances in Neural Information Processing Systems, pp. 1489–1496, 2003.

[42] G. E. Suh, S. Devadas, and L. Rudolph, "A new memory monitoring scheme for memory-aware scheduling and partitioning," in *HPCA*, 2002.

[43] Matthew Wachs et al., "Argon: Performance insulation for shared storage servers," in *FAST*, 2007.

[44] S. Jiang and X. Zhang, "ULC: A file block placement and replacement protocol to effectively exploit hierarchical locality in multi-level buffer caches," in ICDCS, 2004.

[45] Y. Wang and A. Merchant, "Proportional-share scheduling for distributed storage systems," in *FAST*,
2007.

[46] D. Thi´ebaut, H. S. Stone, and J. Wolf, "Improving disk cache hit-ratios through cache partitioning." in IEEE Trans. Computers, 1992.

[47] J. M. Kim et al., "A low-overhead high-performance unified buffer management scheme that exploits sequential and looping references," in *OSDI*, 2000.

[48] C. Gniady, A. R. Butt, and Y. C. Hu, "Program counter based pattern classification in buffer caching,"
in *OSDI*, 2004.