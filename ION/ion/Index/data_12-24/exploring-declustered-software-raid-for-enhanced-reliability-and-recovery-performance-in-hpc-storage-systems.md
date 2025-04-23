# Exploring Declustered Software RAID for Enhanced Reliability and Recovery Performance in HPC Storage Systems

Zhi Qiao∗†, Shuwen Liang†, Hsing-Bung Chen‡, Song Fu†, and Bradley Settlemyer‡

∗Ultrascale Systems Research Center, Los Alamos National Laboratory

† Computer Science and Engineering Department, University of North Texas

‡HPC-DES Group, Los Alamos National Laboratory

*Abstract*—Redundant array of independent disks (RAID) has been widely used to address the reliability and performance issues of storage systems. As the scale of modern storage systems continue growing, disk failure becomes the norm. With the everincreasing disk capacity, RAID recovery based on disk rebuild becomes more and more costly, which causes significant performance degradation and even unavailability of storage systems. Declustered data layout enables parallel RAID reconstruction by shuffling data and parity blocks among all drives (including spares) in a RAID group. However, the reliability and performance of declustered RAID in real-world storage environments have not been thoroughly studied. With the popularity of ZFS file system and software RAID used in production data centers, in this paper, we extensively evaluate declustered RAID with regard to the RAID recovery time and I/O performance on an high performance storage platform at Los Alamos National Laboratory. Our empirical study reveals advantages and disadvantages of the declustered RAID technology. We qualitatively characterize the recovery performance of declustered RAID and compare with that of ZFS RAIDZ under various I/O workloads and access patterns. The experimental results show that the speedup of declustered RAID over traditional RAID is sublinear to the parallelism of recovery I/O. Furthermore, we formally model and analyze the reliability of declustered RAID in terms of the mean-time-to-data-loss (MTTDL) and discover that the improved recovery performance leads to a higher storage reliability compared with the traditional RAID.

*Index Terms*—Storage Reliability, Reliability Modeling, Software RAID, Declustered RAID, Performance Evaluation.

## I. INTRODUCTION

As the scale and complexity of storage systems continue growing, reliability assurance of storage systems becomes more and more imperative but challenging. RAID offers a cost-effective technology to improve the performance and redundancy of storage systems. In a traditional disk array, a number of consecutive disk blocks are grouped into a stripe which stores user data and parity data. Multiple spare drives are kept as standbys in case of disk failures. When a block in a stripe cannot be accessed, all of the other blocks in that stripe are read and used to reconstruct the bad block based on parity computation. Therefore, when a drive fails, data and parity blocks are read from the remaining, operational drives in a RAID array to regenerate all blocks (both data and parity) on the failed drive and write them to a spare drive. This recovery process involves intensive I/O reads and writes and expensive parity computation, which leads to reduced availability and degraded performance of the storage system for user applications and system operations.

Moreover, as the capacity of disk drives grows by 40% per year (i.e., the Kryder's Law), it takes a much longer time to rebuild disk data in a RAID group. For example, the rebuild time for a 4 TB drive is over 10 hours and that for an 8 TB drive can reach several days. Such a prolonged rebuild time leads to possible data loss as additional disk failures are likely to occur during RAID recovery.

A declustered RAID shuffles its data placement in a way that regardless of which disk fails, the recovery workload is distributed among all remaining drives [1]. In addition, spare drives also participate in data read and write by distributing spare blocks among drives in a RAID group. Thus, every drive in a declustered RAID contains data blocks, parity blocks, and spare blocks, and participates in data read, write, and recovery.

The declustered RAID technology is expected to reduce rebuild time and improve storage performance. However, existing works do not provide a thorough study or a deep understanding of the characteristics of declustered RAID in a real-world storage environment. In this research, we comprehensively evaluate both the reliability and performance of the declustered RAID, and compare it against the traditional software RAID (i.e., RAIDZ of the ZFS file system) that is widely used in high performance storage systems such as the Trinity supercomputer at Los Alamos National Laboratory. Specifically, we study the RAID recovery time and I/O throughput by comparing declustered RAID with the results from the RAIDZ. Furthermore, we formulate the mean-timeto-data-loss (MTTDL) for a declustered RAID storage system. Our experimental and analytical results show that the improved recovery performance of the declustered RAID leads to a higher storage reliability compared with traditional RAID.

The main contributions of this paper are as follows.

- To the best of our knowledge, this is the first work that models the reliability and comprehensively characterizes the recovery performance of declustered RAID in a realworld storage environment. Our empirical study compares the performance of declustered RAID and RAIDZ under different I/O access patterns and during RAID recovery. We evaluate the impact of various factors, such as
I/O workload, access pattern, redundancy configuration, and storage utilization, on RAID recovery time and I/O throughput.

- Our study shows that 1) the speedup of declustered RAID over RAIDZ during RAID recovery is sub-linear to the number of drives in a storage pool; 2) the extra overhead caused by permutation-based data shuffling used by declustered RAID is marginal, making the performance of declustered RAID comparable with that of RAIDZ for regular I/O workload; 3) the performance of sequential I/O in declustered RAID is lower than that in RAIDZ for a smaller-scale storage system, suggesting that declustered RAID implementation is a better fit for large-scale systems. Our findings provide valuable insights for understanding the behavior and characteristics of declustered RAID and developing reliable and highperformance storage systems.
- We formally analyze the reliability of declustered RAID using MTTDL. Our analytic results show that the MTTDL of declustered RAID is 3.96 times as high as that of the traditional software RAID, indicating a better storage reliability by using declustered RAID.

The rest of this paper is organized as follows. Section II describes the declustered RAID technology. We characterize the recovery performance of declustered RAID in the face of disk failures in Section III. Reliability modeling of declustered RAID is presented in Section IV. Then, we study the performance of declustered RAID and RAIDZ under various I/O workloads in Section V. The related works are discussed in Section VI. Section VII concludes this paper with remarks on future research.

#### II. DECLUSTERED RAID TECHNOLOGY

#### *A. Software RAID*

RAID provides a "virtualized" storage subsystem that combines multiple physical disk drives into one or more logical groups, aiming to improve storage performance and fault tolerance. In a d + p RAID array, d data blocks and p parity blocks are stored on d + p drives and p disk failures can be tolerated. When a drive fails, all data and parity blocks on the failed drive are reconstructed by using blocks read from d working drives in the same RAID array. To reduce recovery time, the affected RAID array is usually brought offline for rebuild. Online rebuild is feasible but at the cost of degraded performance.

Meanwhile, parallel file systems (PFS) such as Lustre [2], GPFS [3] and BeeGFS [4] have been widely used on highperformance computing (HPC) storage systems. Lustre and BeeGFS use the ZFS as the back-end file system to manage hundreds to thousands of storage nodes. In ZFS, RAIDZ offers a popular and powerful software RAID solution. RAIDZ1, RAIDZ2 and RAIDZ3 provide equivalent redundancy by software as their counterparts, i.e., RAID 5, RAID 6 and RAID 7 by hardware, respectively. Figure 1 illustrates a storage pool which consists of three RAIDZ1 arrays and three shared spare

![](_page_1_Figure_8.png)

Fig. 1: Traditional RAID (e.g., RAIDZ1) vs. declustered RAID (e.g., dRAID1) storage pools. cfg = 3 × (4 + 1) + 3.

drives. In each array, five disk blocks (i.e., four of them are for user data and one is for parities) are grouped into a stripe.

The RAID recovery process in ZFS is called *resilvering*. Resilvering occurs when a drive needs to be replaced due to disk failure or data corruption. During resilvering, data and parities are retrieved (i.e., intensive read) from other working disks in the affected RAIDZ array; reconstruction operations, such as Galois field multiplications (that is compute intensive), are performed to rebuild the lost data and parity blocks; and the recovered data and parity blocks are written to a spare drive (that is I/O write intensive). Resilvering is an expensive operation whose duration depends on the amount of data to be reconstructed and the location of data and parities used in reconstruction. When one or more drives fail during resilvering, data is lost and the RAID array becomes useless.

### *B. Declustered RAID*

Declustered RAID enhances RAID storage systems by distributing data and parities in a stripe (size of G) across a storage pool consisting of C drives where C>G. All drives participate in data read, write, and reconstruction. Figure 1 compares the data layout of three RAIDZ1 arrays and the equivalent declustered RAID arrays. Since data and parities are distributed among drives from multiple arrays, I/O load for resilvering after a disk failure f is spread evenly across (C − f) remaining drives, compared with (G − f) drives in a traditional RAID system. Thus, declustered RAID can enhance a storage system by (1) accelerating the resilvering process and restoration to an operational state, due to parallel recovery I/O, and (2) serving users' I/O requests during resilvering with less performance degradation.

Effective data shuffling is imperative for declustered RAID. Parity declustering [1] uses a layout table to determine the locations of blocks, which causes processing overhead and consumes extra storage space. Random Permutation [5] distributes blocks among drives using a pseudo-random algorithms. However, it cannot guarantee a uniform distribution of stripe blocks. RAID+ [6] employs Latin squares for deterministic addressing instead of using randomized data placement.

TABLE I: Symbols and variables.

| Notation | Description |
| --- | --- |
| d | Number of data blocks per stripe |
| p | Number of parity blocks per stripe |
| k | Number of RAID arrays in a storage pool |
| s | Number of spares in a storage pool |
| cfg | Redundancy configuration |
| C | Size (i.e., number of drives) of a storage pool |
| G | Size of a RAID array, also called stripe size |
| α | Ratio of G/C |
| λ | Disk failure rate |
| f | Number of failed drives |
| δ | Rebuild efficiency of a declustered RAID |
| MTTDL | Mean time to data loss |

However, none of them have been integrated in the official ZFS releases. Their reliability and performance have not been thoroughly studied or fully understood. Permutation development data layout (PDDL) [7] achieves uniform distribution of stripe blocks without using expensive table lookup. The dRAID project [8] implements declustered RAID in ZFS and uses the PDDL algorithm for stripe blocks shuffling.

The PDDL algorithm provides a one-to-one mapping between physical and virtual stripes using Logical Block Addresses (LBA). Initially, PDDL applies a base permutation to randomly shuffle the virtual stripe of LBA0. For the remaining LBAs, the permutation is calculated from the base permutation on-the-fly. For example, LBAi can be derived by adding i to each virtual unit in the base permutation and then modulo the stripe width C. As the preceding computation is light-weight, the derived permutations are not stored in memory. As a result, PDDL incurs a small address translation overhead compared with random data layout algorithms.

Similar to RAIDZ, dRAID supports three redundancy settings, that is dRAID1, dRAID2, and dRAID3 which can tolerate up to 1, 2, and 3 disk failures, respectively. For ease of our discussion, we use *recovery* to refer to resilvering in RAIDZ and rebuild in dRAID, and redundancy configuration cfg = k × (d + p) + s to denote s spares and k RAID arrays each of which has d data drives and p parity drives. Similar to the notations used in [1] and [5], we use C and G to denote the size of a storage pool and the size of a RAID array, respectively. Table I lists the symbols and variables that we use in this paper. In the next section, we investigate the recovery performance of declustered RAID in case of disk failures, and compare with the recovery performance of RAIDZ.

## III. CHARACTERIZING DECLUSTERED RAID RECOVERY FROM DISK FAILURES

An event daemon (called ZED) actively monitors the health status of drives in a storage pool and determines the operation mode in ZFS. When ZED detects a drive fails, it starts a RAID recovery process and throttles application I/O (the degree of throttling is configurable). The intensive read-compute-write operations and massive data movement make the recovery process highly expensive.

In this section, we investigate the performance of declustered RAID during RAID recovery and compare it with the

![](_page_2_Figure_8.png)

Fig. 2: I/O performance degradation during RAID recovery. cfg = 3 × (5 + 2) + 3.

results of RAIDZ. We aim to find out whether the data shuffling and parallel I/O of declustered RAID can shorten the recovery process and by how much compared with RAIDZ. To this end, we test and compare the declustered RAID and RAIDZ under the same storage setting and redundancy configuration. We set the storage pool utilization to 10% and measure the recovery I/O throughput.

#### *A. Storage Platform and Disk Failures*

We set up a storage system at Los Alamos National Laboratory. The platform consists of 10 storage nodes. Each node is equipped with two Intel Xeon E5620 processors (each with 4 cores at 2.4 GHz and 8 threads), 128 GB DDR4 DRAM, and two LSI MegaRAID SAS controller connected to a 45-bay SuperMicro JBOD enclosure via four channels. The overall I/O bandwidth is 24 GB/s, sufficient for aggregated I/O transfer from/to disks. Each JBOD enclosure contains 45 × 4TB perpendicular magnetic recording (PMR) drives. The hardware RAID controller is configured to write-through mode in order to minimize the interference to ZFS I/O writes. As for I/O reads, we employ a read-ahead mode and use 1 GB DDR3 SDRAM cache memory in the hardware controller to further enhance the read performance. Each storage node runs CentOS v7.5 (with the Linux kernel v3.10.0-862) and a ZFS (*zfs-0.7.0-release*) file system.

To incur a disk failure and trigger RAID recovery, we flush out (by writing zeros) the reserved area of ZFS on a drive, which stores the partition table, device label, and RAID configuration and is usually located in the first 1 MB and the last 8 MB on a drive.

#### *B. Storage Performance During Online RAID Recovery*

In this set of experiment, we use fio [9] to produce I/O workload and characterize the performance degradation during RAID recovery. The workloads write and then read a 10 GB file repeatedly with a 50-50 write/read ratio. We then inject a disk failure to a random target drive so the storage pool enters degraded mode. After the RAID is fully recovered, the application workload resumes to normal. This study shows single-workload online RAID recovery under single disk failure event, but the methodology is also applicable to multi-disk failure events in multi-tenant environments.

Figure 2 shows the storage performance during a RAID recovery. Before the failure occurs and after RAID array recovered, the throughput of application I/O is above 1 GB/s for declustered RAID and RAIDZ. When a disk failed at around 1,500 seconds, the I/O throughput of declustered RAID and RAIDZ both declines. In the degraded mode, the application I/O drops to 226 MB/s for declustered RAID and 223 MB/s for RAIDZ, i.e., a 78.5% decrease on average. On the other hand, the recovery time of RAIDZ is 2.21 times longer than that of declustered RAID. In our study, declustered RAID distributes the data, parity, and spare blocks across all 23 (i.e., 3 × (5 + 2) + 3) drives in the storage pool. To recover data on one failed drive, the remaining 22 drives are all involved in data reading, parity calculation, and data writing. In contrast, RAIDZ only uses the 6 remaining drives in the array to rebuild the lost data and the reconstructed data are written to a single spare drive. As a result, the average recovery load for each participant drive in RAIDZ is about 3 times higher than that for a drive in declustered RAID.

The extent of performance degradation between declustered RAID and RAIDZ is comparable, which is different from the intuition that declustered RAID should impose less performance degradation. Our further analysis reveals that ZFS throttles application I/O for a faster RAID recovery by default. This allows declustered RAID to recover data in a shorter period of time than RAIDZ. However, in a declustered RAID, data is striped across multiple arrays in a storage pool. A degraded RAID array compromises the performance of the entire storage pool. In contrast, when RAIDZ performs resilvering, access requests to data on the failed drive are serviced by other drives in the same array on-the-fly. This makes performance degradation confined to the affected array. Thus, their overall performance degradation is comparable. We also note users can change the configuration of ZFS to prioritize application I/O during RAID recovery, which can mitigate the performance degradation of declustered RAID. The recovery process, however, will take more time.

#### *C. RAID Recovery Performance*

When disk failures occur, ZED initiates the RAID recovery process. First, ZFS scans the entire storage pool to check any potential issues. Then, RAIDZ starts to reconstruct data before writing them to spare drives. Declustered RAID, on the other hand, writes reconstructed data to distributed spare blocks. At the end of the recovery process, both schemes report the amount of data recovered in Gigabyte (i.e., GBrecover) and the duration of the recovery process (i.e., timerecover) in a Hour : M inute : Second format, which can be used to compute the recovery throughput.

The speed of data recovery is important for storage reliability as longer recovery time leads to a higher risk of data loss. In the preceding section, we characterize the overall recovery time by declustered RAID and RAIDZ under a fixed setting (as shown in Figure 2). In this section, we conduct a comprehensive analysis of the RAID recovery performance by investigating the impact from various factors.

*1) Sensitivity to Storage Utilization:* In hardware RAID, the information of logical data organization is not available

![](_page_3_Figure_6.png)

Fig. 3: RAID recovery time for a 4-TB failed drive with varying disk utilization. The shorter recovery time, the better. cfg = 3 × (1 + 1) + 1.

![](_page_3_Figure_8.png)

Fig. 4: RAID recovery throughput with an increased number of redundant groups (i.e., varying k), cfg = k × (5 + 2) + 2.

to the underlying volume management. As a result, when a drive fails, data on all sectors (even without valid data) are recovered, which is not cost-effective. ZFS integrates functions of the file system and logical volume manager, making the recovery process aware of data layout. Thus, only active data are recovered instead of entire-drive recovery. In our recent study [10], we measured the recovery time of a 2-TB drive by using hardware RAID and software RAID. The former took six hours, while the latter took only minutes when the drive's storage utilization was low (e.g., 5%).

Figure 3 plots the recovery time of declustered RAID and RAIDZ under different storage utilization. Both RAID schemes are aware of data layout in a storage pool and recover the active data only. For a 4 TB drive, when the storage utilization is 30%, 60%, and 90%, the amount of active data to be recovered is 832 GB, 1930 GB, and 2770 GB, respectively. From the figure, we can see that it takes RAIDZ 8.82 hours to recover 2770 GB active data, and by comparison declustered RAID's recovery time is only 3 hours (i.e., 65.9% less). On average, declustered RAID is 2.89 times as fast as RAIDZ in recovering lost data.

We also evaluate the degree of throughput degradation between declustered RAID and RAIDZ. When the storage utilization increases from 30% to 90%, RAIDZ's recovery throughput drops by 10.5%, from 97.5 MB/s to 87.2 MB/s. As a comparison, declustered RAID's recovery throughput decreases by 11.8%, from 285.4 MB/s to 251.5 MB/s. Based on the impact analysis of storage utilization on I/O throughput in Section V-B (i.e., Figure 8), we attribute the recovery throughput degradation to the deteriorated I/O performance, as data reconstruction is read and write intensive.

*2) Sensitivity to Redundancy Configuration:* To characterize sensitivity of recovery performance to redundancy configuration under disk failure, we vary the value of d, p, and k in redundant configuration cfg = k × (d + p) + s. Since the recovery load of declustered RAID is distributed across all the remaining drives, the data recovery bandwidth becomes the aggregated I/O of (C − f) drives in the storage pool, where C = k ∗ (d + p) + s and f is the number of failed drives. For RAIDZ, its recovery load is shared by (G−f) surviving drives for reading data and f spare drives for writing data, where G = d + p. Therefore, the ratio of the recovery bandwidth for both data read and write between dRAID and RAIDZ can be approximated by C−f G−f . Since f is much smaller than C or G, the ratio becomes C G = k+ s d+p . As (d+p) is usually multiple times greater than s, the value of k (i.e., the number of RAID arrays in a storage pool) becomes critical for understanding the recovery performance of declustered RAID. Due to page limitation, we only present the sensitivity results of recovery I/O performance to k in this paper.

Figure 4 shows the recovery throughput of dRAID and RAIDZ as k increases from 1 to 6. For each value of k, we measure the rebuild throughput of dRAID, and the resilvering throughput of RAIDZ (denoted by T hroughputrebuild, and T hroughputresilvering). From the figure, we can see that the T hroughputrebuild increases by 1.92 times as k changes from 1 to 6. It is 1.47 times to 3.13 timers greater than T hroughputresilvering. For RAIDZ, its resilvering throughput is relatively stable at 93.3 MB/s on average. This is because the change of k does not affect the number of drives involved in data recovery, i.e., (d+p−f) drives for retrieving data and f spares for storing the reconstructed data. We also find that the measured (T hroughputrebuild/T hroughputresilvering) is less than k (that is the theoretical speedup), which indicates the performance improvement gradually decreases as a storage system scales out.

## *D. Efficiency of RAID Recovery*

Muntz et al. [11] used the ratio of (G−1)/(C −1) (denoted by α) to calculate the fraction of remaining drives that are read during data recovery. The parameter α (0 <α< 1), together with C and G, affect the recovery performance, data reliability, and cost-effectiveness of a storage system. When we consider the aggregated recovery I/O bandwidth for f failed drives, the analytical (ideal) speedup of declustered RAID over RAIDZ can be expressed as follows.

$$\alpha_{ideal}=\frac{C-f}{G-f}\tag{1}$$

Empirical results from our experiments, however, indicate that the rebuild performance of declustered RAID (i.e., T hroughputrebuild) cannot reach the ideal speedup. For example, T hroughputrebuild should be 7.17 times as high as T hroughputresilvering for k = 6, whereas our experimental

![](_page_4_Figure_6.png)

Fig. 5: RAID recovery efficiency (δ).

results show the actual speedup is only 3.13. The actual speedup is expressed as

$$\alpha_{actual}=\frac{Throughput_{rebuild}}{Throughput_{reviring}}\tag{2}$$

In our analysis, we use δ to denote the efficiency of RAID recovery by declustered RAID compared with RAIDZ. The value of δ is calculated by

$$\delta=\frac{\alpha_{actual}}{\alpha_{ideal}}=\frac{\frac{d+p}{f}-1}{Throughput_{resilvering}}*\frac{Throughput_{rebuild}}{\frac{k*(d+p)+s}{f}-1}\tag{3}$$

where $k*$ is the number of 

where k∗(d+p)+s f and d+p f are the inverse of the number of failed drives in a declustered storage pool and a RAIDZ array.

Figure 5 shows the measured recovery efficiency (δ) with increasing number of disks per stripe k and number of drives C. The ideal recovery efficiency is 1.0. Our experimental results show δ decreases from 1.1 to 0.4 as k and C increase, which implies a decreasing recovery efficiency when a storage system scales out. For declustered RAID, issues like the lack of spatial locality and congested I/O traffic affect the recovery efficiency. Meanwhile, some recovery workloads are data dependent and the communication overhead also increases as k and C increase.

We find that δ = 1.1 when (k, C) = (1, 9), which exceeds the ideal efficiency. This can be explained as follows. In RAIDZ, the resilvering process scans the entire block tree before recovering data blocks. This process generates bursty random I/Os, which affects the performance of resilvering. In contrast, current implementation of declustered RAID does not scan the block tree to verify checksum and its rebuild operations are executed in parallel across multiple arrays. We also notice that δ increases slightly when (k, C) = (6, 44). This is because the throughput of dRAID rebuild (T hroughputrebuild) continuously increases as the number of disks per stripe k increases, while the throughput of RAIDZ resilvering (T hroughputresilvering) begins to decrease when k is 6, as shown in Figure 4. An increase of the throughput ratio (i.e., T hroughputrebuild/T hroughputresilvering) at k = 6 outweighs that of k. According to Equation (3), the recovery efficiency has a slight increase.

Overall, declustered RAID benefits from a higher parallelism of recovery I/O. The recovery duration of declustered

![](_page_5_Figure_0.png)

Fig. 6: A m-drive Markov model.

RAID is only a fraction of that of RAIDZ. We also discover that as the storage system scales out, the speedup of recovery performance by declustered RAID slows down and the efficiency of data reconstruction drops until the performance gain from parallel I/O surpasses the overhead from a larger scale.

#### IV. RELIABILITY MODELING AND ANALYSIS OF DECLUSTERED RAID

For dRAIDm and RAIDZm, m ∈ {1, 2, 3}, when m + 1 or more drives fail in a disk array, we consider the array as failed and data are lost. In such a case, we may recover the array by using the most recent backup if it exists.

Mean-time-to-data-loss (MTTDL) is widely used to analyze the reliability of storage systems. It uses Markov models to describe the transition of storage's health status. We assume the failure rates of drives are independent of time and identically distributed random variables as described in [12]. The disk failure rate and recovery rate are denoted by λ and μ respectively. We assume a storage system immediate reconstructs data on hot-standby spare drives upon detecting disk failures [11].

Figure 6 shows a Markov model for a m-disk fault-tolerant storage system. In the figure, each state in a circle indicates the number of failed drives in an array. Initially (In State 0), all G drives in the array are operational. With a probability of G·λ, the system transitions to State 1 and stays for ((G−1)·λ+μ)−1 hours. The system then transitions to State 2 with a probability of (G−1)·λ (G−1)·λ+μ. This process repeats until the system transitions from State m to the data loss (DL) state. Declustered RAID and RAIDZ explore parallel I/O to reconstruct data. When data from all failed drives are recovered, the storage system goes back to the initial state (State 0).

We use the annual failure rate (AFR) supplied by drive manufacturers to calculate the failure rate λ and mean-timebetween-failure (MTBFdisk) as Tλ = λ−1. From our experimental results, we derive the mean-time-to-recovery as Tμ = μ−1. Then the MTTDL of an array can be expressed as a function of Tλ and Tμ.

$$MTTDL_{array}=\frac{T_{\lambda}}{G}*\frac{1}{1-e^{-T_{\mu}\left(\frac{T_{\lambda}}{G-1}\right)-1}}*\cdots*\frac{1}{1-e^{-T_{\mu}\left(\frac{T_{\lambda}}{G-m}\right)-1}}$$ $$=\frac{T_{\lambda}}{G}\prod_{i=1}^{m}\frac{1}{1-e^{-\frac{T_{\mu}\left(G-i\right)}{T_{\lambda}}}}\approx\frac{T_{\lambda}}{G}\prod_{i=1}^{m}\frac{T_{\lambda}}{T_{\mu}\left(G-i\right)}$$

We can then derive the MTTDL of the storage pool as

$$\begin{array}{r l}{M T T D L_{p o o l}}&{{}={\frac{M T T D L_{a r r a y}}{k}}={\frac{G(M T T D L_{a r r a y})}{C}}}\\ {\ }&{{}\approx{\frac{T_{\lambda}}{C}}\prod_{i=1}^{m}{\frac{T_{\lambda}}{T_{\mu}(G-i)}}}\end{array}$$

The preceding equation shows that MTTDLpool is inversely proportional to the recovery time Tμ. To compare the reliability of declustered RAID and RAIDZ under the similar redundancy configuration, we set parameters such as Tλ, m, C and G to the same values for the two RAID schemes.

We calculate the MTTDL of declustered RAID over RAIDZ by using the experimental results presented in Figure 4, where cfg = 6 × (5 + 2) + 2. We adopt the best estimate of realworld AFR as 0.97%, which is reported by BackBlaze [13] and calculate λ using the equation AF R = 1 − exp(−8766/λ), where 8766 is the number of hours in a year. The MTTDL of the declustered RAID pool with 44× 4-TB drives is 1092.18 years, and the MTTDL of the RAIDZ pool is 275.58 years. MTTDLdRAID/MT T DLRAIDZ = 3.96, that is the declustered RAID pool is more reliable than the RAIDZ pool.

We note that some assumptions that are used are not always the case in production systems. For instance, the failure rate of drives may vary and it may be time-dependent. In comparison of the two RAID schemes, these variables eventually cancel out. We also note that the absolute value of MTTDL (i.e., 1092.18 years and 275.58 years) of a RAID storage system is meaningless, as the mission time of a production storage system is only 5 to 10 years. The the ratio of the two MTTDLs (i.e., 3.96) provides a valuable metric to compare the reliability of two RAID storage systems, according to the related studies, such as [14], [15].

## V. STORAGE PERFORMANCE WITH DECLUSTERED RAID

To characterize the behavior of declustered RAID, we run I/O benchmark programs on our storage platform and evaluate the I/O performance under varying data access patterns, storage utilization, and redundancy configurations.

#### *A. I/O Performance*

We employ IOzone [16], a widely used I/O benchmark program, to evaluate declustered RAID and RAIDZ. IOzone uses low-level C-library I/O operations as a load generator and profiles a storage systems with varying file sizes and access patterns. We comprehensively evaluate declustered RAID and RAIDZ under sequential and random I/O using small and burst workloads. These synthetic workloads simulate both compute and I/O-intensive applications.

Figure 7 shows the I/O throughput of a triple-parity declustered RAID (i.e., dRAID3) under ten I/O workloads and varying load sizes. The configuration of the declustered RAID is cfg = 3×(8 + 3) + 3, i.e., 3 RAID groups with each group using 8 data blocks and 3 parity blocks and 3 shared spare drives. We change the load size from 16 MB to 128 GB while testing the following I/O workloads.

- *Sequential writes*: data are sequentially written to a new file.
- *Sequential rewrites*: data are rewritten sequentially to an existing, recently used file.
- *Sequential reads*: data are sequentially read from an existing file.
- *Sequential rereads*: data are reread sequentially from an existing, recently accessed file.

![](_page_6_Figure_0.png)

Fig. 7: I/O behavior of a triple-parity declustered RAID. cfg = 3 × (8 + 3) + 3.

- *Random reads/writes*: Data are read and written by using random offsets.
- *Fread/Fwrite*: Calling fread() and fwrite() functions so data are read from and written to a new file in a stream and are buffered in memory.
- *Re-fread/Re-fwrite*: A recently used file is read from and written to by calling fread() and fwrite().

From Figure 7, we can see that the throughput of readrelated programs exhibits a stepped degradation as the load size increases. Specifically, the throughput of read-related programs drops in three stages, i.e., 3.7 GB/s on average in the first stage, 1.7GB/s (i.e., 54.1% decrease) in the second stage, and 250 MB/s (i.e., 85.3% decrease) in the last stage. We study how ZFS processes the read-related load to understand this performance characteristic. ZFS buffers I/O for data transfer between applications and the storage system. In addition to the on-core buffer, ZFS employs an Adaptive Replacement Cache (ARC) [17] which consists of DRAM as the off-core cache. The caching effect plays a major role during the first and second stages of the read-related workloads. Applications leverage caching to reduce access latency. Moreover, as we discuss in Section III-A, caching by the RAID controller provides additional performance improvement, especially for sequential reads. Both ARC and RAID controller's cache influence the I/O throughput during the first stage. As the load size exceeds the capacity of the hardware RAID controller's cache (i.e., 1 GB), only ARC effectively caches data during the second stage. Eventually, ARC is used up, and read-intensive workload cannot further take advantage of the temporal and spatial locality from the available cache. Note that a Level-2 ARC (L2ARC) device uses dedicated SSDs as a secondary cache, which can further boost the read throughput. In our experiments, however, we do not use L2ARC devices as we aim to measure the real throughput of a software RAID array.

Figure 7 also shows that the performance of write-related programs decreases monotonically, that is from 1.3 GB/s when the load size is 16 MB, to 700 MB/s when the load size increases to 128GB. This is because ZFS buffers data (under default setting) before periodically writing them to the persistent storage, and as a write load exceeds the cache's capacity, the turnaround time of asynchronous writes is prolonged. Since the RAID controller is configured to a write-through mode, the cache is not used, which allows us to measure the throughput of asynchronous writes in ZFS. When synchronous writes are performed, the I/O throughput is degraded by 40% to 50%. We also find that ZFS keeps tracking data integrity by using ZFS Intent Log (ZIL) in order to prevent data loss caused by system failures and power outages. In production systems, a dedicated flash device is used for ZIL, known as SLOG.

For comparison, we benchmark RAIDZ using IOzone under a similar configuration, i.e, cfg = 3 × (8 + 3) + 3. The experimental results are similar to those in Figure 7. Due to space limitation, we do not include the results in the paper. A RAIDZ array uses a subset of drives, while declustered RAID involves all drives (including spares) in a storage pool. On the other hand, the declustered RAID adopts a more complex shuffling scheme, which incurs additional mapping overhead. Their performance deviates when more storage space is used. The results are presented in the following section.

#### *B. Sensitivity to Storage Utilization*

We study the sensitivity of the performance of declustered RAID and RAIDZ to storage utilization. We use the configuration cfg = 3 × (d + 1) + 1, where d = {1, 2}. The reason of using a small stripe width, i.e., G = {2, 3}, is that it takes a long time to exhaust disk space for a storage pool with a large stripe width. For example, filling 70% of a 85 TB storage pool with a (3 × (8 + 3) + 3) configuration takes more than 60 hours. A smaller stripe width enables us to evaluate the performance of declustered RAID and RAIDZ under different storage utilization in a cost-effective fashion, that is about 10 times faster. In the following experiments, we first allocate

![](_page_7_Figure_0.png)

Fig. 8: I/O throughput of declustered RAID and RAIDZ as the storage utilization increases (cfg = 3 × (2 + 1) + 1). Bold curves represent the trends of the average throughput by using the first-order polynomials.

a large random file on local file system that occupies 1% of storage space. We then write this file to the declustered RAID and RAIDZ using use dd, then read it back to /dev/null. This process is repeated until an expected portion of storage space (for instance 70%) is occupied.

Figure 8 shows the performance of declustered RAID and RAIDZ under the same configuration. As the storage utilization changes from 0% to 70%, the I/O throughput first drops, then surges (around 40%-50% utilization), and drops again. The throughput degradation at the lowest point is 18% and 6% for declustered RAID and RAIDZ, respectively. As more storage space is used, it takes extra time to locate data. In addition, the more fragmentation makes space management slower. Declustered RAID maintains a more complicated data layout structure than RAIDZ, and as a result, its I/O performance is more sensitive to storage utilization. The experimental results show that the performance of declustered RAID is 38.6% lower than that of RAIDZ on average. Recall that the shuffled data layout in declustered RAID improves the aggregated recovery I/O parallelism, but compromises data spatial locality (as described in Section II). In this experiment, we use dd which writes and reads data sequentially to/from the storage. Compared with RAIDZ, declustered RAID allocates and retrieves fewer continuous data blocks per disk spindle and thus takes a longer data access time. We also observe that the performance gap between declustered RAID and RAIDZ reduces as the stripe width increases, which is shown in Figure 9a.

To address this performance issue of dRAID, we plan to enhance its spatial data locality by leveraging data prefetching. Another solution is to increase the block size, which will also allow dRAID to retrieve more continuous data per disk spindle. We will evaluate the performance gain and possible overhead of these approaches and find the mechanism and setting that lead to the best result.

When the storage utilization increases, the performance difference between declustered RAID and RAIDZ (i.e. T hroughputRAIDZ − T hroughputdRAID) displays a standard deviation of 77.99, which is 9.8% of the average I/O throughput. On the other hand, the performance variance of T hroughputRAIDZ is 13.8%, which is higher than (T hroughputRAIDZ − T hroughputdRAID). This indicates that declustered RAID and RAIDZ have similar performance characteristics when the storage utilization increases, but the performance variance of each one of them is relatively higher.

We observe that the performance of declustered RAID and RAIDZ increases by about 30% at around 40%-50% utilization. This phenomenon is the result of interaction among multiple factors, including data access pattern, data layout, data locality, and physical properties of drives. The data layout at certain utilization matches the data access patterns better, which leads to a better data locality and a higher throughput. The physical properties and conditions of drives can affect where such a performance rise appears. For example, we have conducted the same experiment on a different set of drives and the throughput surge happens when the storage utilization is around 30%.

## *C. Sensitivity to Redundancy Configuration*

The configuration of RAID group affects the data access pattern. For example, increasing the ratio of the number of data blocks to that of parity blocks in an array can improve the I/O throughput due to higher I/O parallelism. Adding more parities to a stripe may sacrifice data access performance for reliability. To characterize such impact, we configure the storage platform with diverse redundancy settings and evaluate the performance of both declustered RAID and RAIDZ. The three configuration parameters that we change in the settings are the number of data blocks (d) per stripe, the number of parity blocks (p) per stripe, and the number of stripes (k) per storage pool.

Figure 9 shows the influence of d, p, and k on the I/O throughput of the declustered RAID and RAIDZ. In the following subsections, we characterize the impact of the three configuration parameters on the storage performance.

*1) The Number of Data Blocks Per Stripe (*d): Increasing d in a stripe not only provides more storage space for user data, but also enhances I/O parallelism of a disk array. User data are mapped to stripes during *data striping*, and then for each array, data are distributed across drives. As d increases, more drives are involved in data storage, which improves I/O parallelism and throughput.

In this set of experiments, we create a storage pool with configuration cfg = k ×(d+p) +s, where k = 3, p = s = 2, and d ∈ [4, 12]. Figure 9a shows the I/O throughput with varying d. In the figure, we can see that the write throughput of RAIDZ is relatively stable, reaching around 660 MB/s as d increases. In comparison, the write performance of the declustered RAID gradually increases from 480 MB/s to approaching RAIDZ's throughput when d ≥ 9.

In Figure 9a, we also find that counter-intuitively the read throughput of both declustered RAID and RAIDZ drops (by 86.1% and 79.6% respectively) as d is increased from 4 to 12. A possible explanation of this performance degradation is that the increase of d compromises spatial locality of user data causing lower read bandwidth. Despite the opposite trends

![](_page_8_Figure_0.png)

Fig. 9: Throughput of declustered RAID and RAIDZ with varying d, p, and k under configuration k × (d + p) + s.

of the write and read performance, the overall performance (i.e., T hroughputwrite+T hroughputread) of the declustered RAID is close to that of RAIDZ, as the difference of the overall performance between declustered RAID and RAIDZ is within 18%.

*2) The Number of Parity Blocks Per Stripe (*p): The number of parity blocks in a stripe determines the capability of fault tolerance. As p increases, the data-parity ratio (d/p) decreases. Thus, the I/O bandwidth used for data accesses also reduces.

We create a storage pool with cfg = k × (d + p) + s, where k = 3, d = 5, and s = 1. Unlike erasure-coding schemes [18] that can work with any number of parity blocks, declustered RAID and RAIDZ only support p in the range of [1, 3]. Figure 9b shows the influence of p on the read and write performance. In the figure, we find that the write throughput of declustered RAID is on average 28.3% less than that of RAIDZ, while reads in declustered RAID outperform those in RAIDZ when p ≥ 2. The overall performance (i.e., T hroughputwrite + T hroughputread) of declustered RAID is close to that of RAIDZ and the performance difference is within 15.4%.

*3) The Number of Arrays Per Storage Pool (*k): In a storage pool with multiple RAID arrays, data are stripped across the arrays. The overall write bandwidth increases when k becomes larger. To quantify the impact of the stripe size on the I/O performance of a storage pool, we employ a 5:1 data-parity ratio for each of the k arrays, where k ∈ [1, 7], and set s = 1, i.e., one global spare drive. This configuration is referred to as RAID 50, that is striping (RAID 0) over multiple RAID-5 arrays. Figure 9c plots the performance results. In the figure, we can see that both declustered RAID and RAIDZ achieve a better write throughput as k is increased from 1 to 2. For k ≥ 2, the performance improvement becomes flat. On average, the write performance of declustered RAID is 26.6% less than that of RAIDZ.

The read throughput of declustered RAID is almost the same as that of RAIDZ at the beginning, then becomes lower and finally flats as k increases. This is caused by the reduced per spindle read bandwidth for declustered RAID. The overall performance (i.e., T hroughputwrite + T hroughputread) of declustered RAID and RAIDZ is close with a difference within 5.6%.

The major findings from experiments described in this section are as follows. 1) The performance of declustered RAID and RAIDZ is similar for different types of workload when the file size is smaller than the memory capacity. 2) As the storage utilization increases, both declustered RAID and RAIDZ suffer from performance degradation. 3) When load size exceeds the memory capacity, the T hroughputwrite of declustered RAID becomes worse than that of RAIDZ, while T hroughputread of declustered RAID exhibits an opposite trend. *The overall performance (*T hroughputwrite + T hroughputread*) of declustered RAID is comparable with that of RAIDZ when there is no disk failure.*

#### VI. RELATED WORKS

To improve the storage reliability, a number of existing research aims to improve the reconstruction performance through task scheduling, for example [19], [20], [21]. Other approaches such as [22], [23], [24] address RAID reconstruction issues by utilizing higher sequential bandwidth to accelerate RAID recovery. Research has also been performed to mitigate the performance degradation during RAID recovery. Tsai et. al. [25] presented a RAID organization called multipartition RAID to reduce the performance degradation during RAID rebuilds. In [26], workloads on degraded RAID sets were outsourced to surrogate RAID sets. Meanwhile, there are recent works that leveraged machine learning technologies to manage disk failures proactively. Clustering and regressionbased disk degradation signatures [27], [28], Support Vector Machine (SVM) [29], probability analysis [30], regression trees [31], and correlation analysis on SSDs [32] have been proposed to model and predict disk failures.

Muntz et. al. first proposed a parity declustering layout [7]. Their work was further evaluated and extended in [33], [34], [1]. However, randomized data placement in these works produces an uneven distribution of I/O accesses and RAID recovery workload. The PDDL algorithm [7], as discussed in Section II-B, incorporates randomization and permutation to generate an uniform data layout and incurs little overhead.

In addition to dRAID, systems such as IBM XIV [35], Flat Datacenter Storage [36], and Ceph's CHUSH [37] also apply declustered data layout. They use pseudo-random algorithms to realize efficient and uniform data distribution. RAID+ [6] employs deterministic addressing. ZFS has been widely used and tested in production systems. We believe the integration of declustered RAID in ZFS will significantly improve its reliability and adoption for building high-performance and reliable storage systems.

#### VII. CONCLUSIONS

Declustered RAID provides a new way to distribute data across RAID arrays and reconstruct lost data when drive fails. In this work, we comprehensively evaluate and model the storage reliability and performance including RAID recovery time and throughput on a real-world storage platform. Our experimental results show that declustered RAID significantly reduces RAID recovery time. The speedup is sub-linear with regard to the number of drives involved in parallel I/O for RAID recovery. Furthermore, the improved recovery performance leads to a higher storage reliability.

We also note that declustered RAID has certain limitations. For example, shuffling of data blocks oblivious to spacial locality in declustered RAID affects the performance of normal I/O operations. The current implementation of declustered RAID skips checksum verification during RAID rebuilds, which may overlook data corruptions and cause soft errors. It is not our intention to replace RAIDZ with dRAID in this paper. As an ongoing work, we are developing methods and software to address the aforementioned issues.

#### ACKNOWLEDGMENT

We thank our shepherd Dr. Kostas Magoutis and the anonymous reviewers for their invaluable feedback that greatly improved the presentation of this paper. This work was supported in part by an NSF grant CCF-1563750 and an LANL grant. Los Alamos National Laboratory is supported by the U.S. Department of Energy contract DE-AC52-06NA25396. This paper has been assigned a LANL identifier LA-UR-19-27660.

#### REFERENCES

- [1] M. Holland and G. A. Gibson, "Parity declustering for continuous operation in redundant disk arrays," in *ACM ASPLOS*, 1992.
- [2] OpenSFS and EOFS., "Lustre File System," 2019. [Online]. Available: http://lustre.org/
- [3] F. Schmuck and R. Haskin, "GPFS: A shared-disk file system for large computing clusters," in *USENIX FAST*, 2002.
- [4] ThinkParQ and the Fraunhofer Center for High Performance Computing, "BeeGFS," 2019. [Online]. Available: https://www.beegfs.io/content/
- [5] A. Merchant and P. S. Yu, "Analytic modeling of clustered RAID with mapping based on nearly random permutation," *IEEE Transactions on Computers*, vol. 45, no. 3, pp. 367–373, 1996.
- [6] G. Zhang, Z. Huang, X. Ma, S. Yang, Z. Wang, and W. Zheng, "RAID+: Deterministic and balanced data distribution for large disk enclosures," in *USENIX FAST*, 2018.
- [7] T. J. Schwarz, J. Steinberg, and W. A. Burkhard, "Permutation development data layout (PDDL)," in *IEEE HPCA*, 1999.
- [8] I. Huang, "The dRAID project," 2018. [Online]. Available: https: //github.com/zfsonlinux/zfs/wiki/dRAID-HOWTO
- [9] J. Axboe *et al.*, "Flexible I/O Tester," 2019. [Online]. Available: https://github.com/axboe/fio
- [10] Z. Qiao, J. Hochstetler, S. Liang, S. Fu, H.-b. Chen, and B. Settlemyer, "Incorporate proactive data protection in ZFS towards reliable storage systems," in *IEEE DataCom*, 2018.
- [11] R. R. Muntz and J. C. Lui, *Performance analysis of disk arrays under failure*. Department of Computer Science , University of California, 1990.

- [12] K. M. Greenan, J. S. Plank, and J. J. Wylie, "Mean time to meaningless: Mttdl, markov models, and storage system reliability." in *HotStorage*, 2010.
- [13] BackBlaze, "How long do hard drives last: 2018 hard drives stats," Jun 2018. [Online]. Available: https://www.backblaze.com/blog/ hard-drive-stats-for-q1-2018/
- [14] A. Amer, D. D. E. Long, and S. J. Thomas Schwarz, "Reliability challenges for storing exabytes," in *IEEE ICNC*, 2014.
- [15] F. Machida, R. Xia, and K. S. Trivedi, "Performability modeling for raid storage systems by markov regenerative process," *IEEE Transactions on Dependable and Secure Computing*, vol. 15, no. 1, pp. 138–150, 2018.
- [16] W. Norcott, D. Capps *et al.*, "Iozone filesystem benchmark," 2019. [Online]. Available: http://iozone.org/
- [17] N. Megiddo and D. S. Modha, "ARC: A self-tuning, low overhead replacement cache." in *USENIX FAST*, 2003.
- [18] H. Chen and S. Fu, "Parallel erasure coding: Exploring task parallelism in erasure coding for enhanced bandwidth and energy efficiency," in *IEEE NAS*, 2016.
- [19] C. R. Lumb, J. Schindler, G. R. Ganger, D. F. Nagle, and E. Riedel, "Towards higher disk head utilization: extracting free bandwidth from busy disk drives," in *USENIX OSDI*, 2000.
- [20] E. Thereska, J. Schindler, J. Bucy, B. Salmon, C. R. Lumb, and G. R. Ganger, "A framework for building unobtrusive disk maintenance applications," in *USENIX FAST*, 2004.
- [21] M. Wachs, M. Abd-El-Malek, E. Thereska, and G. R. Ganger, "Argon: Performance insulation for shared storage servers." in *USENIX FAST*, 2007.
- [22] J. Y. B. Lee and J. C. S. Lui, "Automatic recovery from disk failure in continuous-media servers," *IEEE Transactions on Parallel and Distributed Systems*, vol. 13, no. 5, pp. 499–515, 2002.
- [23] Q. Xin, E. L. Miller, and T. J. E. Schwarz, "Evaluation of distributed recovery in large-scale storage systems," in *ACM HPDC*, 2004.
- [24] T. Xie and H. Wang, "MICRO: A multilevel caching based reconstruction optimization for mobile storage systems," *IEEE Transactions on Computers*, vol. 57, no. 10, pp. 1386–1398, 2008.
- [25] W.-J. Tsai and S.-Y. Lee, "Multi-partition raid: A new method for improving performance of disk arrays under failure," The *Computer Journal*, vol. 40, no. 1, pp. 30–42, 1997.
- [26] S. Wu, H. Jiang, D. Feng, L. Tian, and B. Mao, "Improving availability of RAID-structured storage systems by workload outsourcing," *IEEE Transactions on Computers*, vol. 60, no. 1, pp. 64–79, 2011.
- [27] S. Huang, S. Liang, S. Fu, W. Shi, D. Tiwari, and H. bung Chen, "Characterizing disk health degradation and proactively protecting against disk failures for reliable storage systems," in *IEEE ICAC*, 2019.
- [28] S. Huang, S. Fu, Q. Zhang, and W. Shi, "Characterizing disk failures with quantified disk degradation signatures: An early experience," in *IEEE IISWC*, 2015.
- [29] J. F. Murray, G. F. Hughes, and K. Kreutz-Delgado, "Hard drive failure prediction using non-parametric statistical methods," in *ICANN/ICONIP*, 2003.
- [30] A. Ma, R. Traylor, F. Douglis, M. Chamness, G. Lu, D. Sawyer, S. Chandra, and W. Hsu, "RAIDShield: characterizing, monitoring, and proactively protecting against disk failures," *ACM Transactions on Storage*, vol. 11, no. 4, p. 17, 2015.
- [31] J. Li, X. Ji, Y. Jia, B. Zhu, G. Wang, Z. Li, and X. Liu, "Hard drive failure prediction using classification and regression trees," in *IEEE/IFIP* DSN, 2014.
- [32] S. Liang, Z. Qiao, J. Hochstetler, S. Huang, S. Fu, W. Shi, D. Tiwari, H. Chen, B. Settlemyer, and D. Montoya, "Reliability characterization of solid state drives in a scalable production datacenter," in *IEEE Big Data*, 2018.
- [33] G. A. Alvarez, W. A. Burkhard, and F. Cristian, "Tolerating multiple failures in RAID architectures with optimal storage and uniform declustering," in *ACM SIGARCH*, 1997.
- [34] S.-C. Chau and A. W.-C. Fu, "A gracefully degradable declustered RAID architecture with near optimal maximal read and write parallelism," in *IEEE CLUSTER*, 2000.
- [35] IBM, "IBM XIV storage system architecture and implementation," 2017, http://www.redbooks.ibm.com/redbooks/pdfs/sg247659.pdf.
- [36] E. B. Nightingale, J. Elson, J. Fan, O. Hofmann, J. Howell, and Y. Suzue, "Flat datacenter storage," in *USENIX OSDI*, 2012.
- [37] S. A. Weil, S. A. Brandt, E. L. Miller, and C. Maltzahn, "Crush: Controlled, scalable, decentralized placement of replicated data," in *IEEE SC*, 2006.

