# **Predicting Disk I/O Time of HPC Applications on Flash Drives**

Mitesh R. Meswani, Pietro Cicotti, Jiahua He, and Allan Snavely

*San Diego Supercomputer Center, University of California, San Diego, CA, USA*

mitesh@sdsc.edu, pcicotti@acm.org, jiahua@gmail.com, allans@sdsc.edu

*Abstract*— **As the gap between the speed of computing elements and the disk subsystem widens it becomes increasingly important to understand and model disk I/O. While the speed of computational resources continues to grow, potentially scaling to multiple peta flops and millions of cores, the growth in the performance of I/O systems lags well behind. In this context, data-intensive applications that run on current and future systems depend on the ability of the I/O system to move data to the distributed memories. As a result, the I/O system becomes a bottleneck for application performance. Additionally, due to the higher risk of component failure that results from larger scales, the frequency of application checkpointing is expected to grow and put an additional burden on the disk I/O system [1].**

**Emergence of new technologies such as flash-based Solid State Drives (SSDs) presents an opportunity to narrow the gap between speed of computing and I/O systems. With this in mind, SDSC's PMAC lab is investigating the use of flash drives in a new prototype system called DASH [8, 9, 13]. In this paper we apply and extend a modeling methodology developed for spinning disk and use it to model disk I/O time on DASH. We studied two data-intensive applications, MADbench2 [6] and an application for geological imaging [5]. Our results show that the prediction errors for total I/O time are 14.79% for MADbench2 and our efforts for geological imaging yield error of 9% for one category of read calls; this application made a total of 3 categories of read/write. We are still investigating the geological application, and in this paper we present our results thus far for both applications.**

*Keywords-Modeling; Performance; HPC; I/O;* 

# I. INTRODUCTION

In this paper we present a methodology to predict an applications' disk I/O time. Our methodology consists of the following three steps: (1) characterize an application's I/O characteristics on a reference system. (2) Using a configurable I/O benchmark, collect statistics on the reference and target systems about the I/O operations that are relevant to the application. (3) Calculate a ratio between the measured I/O performances of the application on the reference system with respect to target systems to predict the applications' I/O time on the target systems without actually running the application on the target system. This *cross-platform* prediction can greatly reduce the effort needed to characterize the I/O performance of an application across a wide set of machines and can be used to predict the I/O performance of the application on systems that have not been built. The cornerstone of this approach is that the I/O operations in the application have to be measured once on the reference system. The target systems then need only to be characterized by how well they can perform certain fundamental I/O operations, from which we can predict the I/O performance of the application on the target system.

We evaluate our methodology by predicting the total I/O time of MADbench2 and a geological imaging application. We use IOR to characterize I/O operations of MADbench2 and write our own benchmark to characterize operations of the geological imaging application on target systems. Our results show our methodology has prediction errors in the range of 8.59% to 20.66%, and thus far our modeling effort for the geological imaging application has resulted in error of 9% for reads of size 0.72MB per call; we are still modeling two more read and three write categories. Our results thus far indicate, that low prediction error can be realized with large size reads/writes; however, modeling smaller size reads/writes requires further investigation. The rest of the paper is organized as follows: Section 2 gives an overview of our I/O performance prediction methodology. Section 3 describes the workloads and systems used for evaluation of the methodology and Section 4 presents the results of our evaluation. Section 5 presents conclusions and future work and finally, Section 6 presents related work.

# II. METHODOLOGY

Given an application, a reference system, and target systems for which prediction is required, figure 1 shows the modeling and prediction workflow used in our experiments. As shown in this figure, using PEBIL [2], a binary instrumentation tool developed in-house, we first instrument all I/O calls in the application. The instrumented application is then executed on the reference system and the application's I/O profile is stored for further analysis. The profile contains the time spent in all I/O calls. Additionally, we also collect data that pertains to each call, for example, we collect data size for read/write calls, and for seeks we collect the seek distance. Next, for each I/O call we simulate its execution using I/O micro benchmarks such as IOR [3]. We collect the time spent by the I/O micro benchmark on the reference system and target systems. An I/O ratio is calculated as shown in equation 1. This ratio is our prediction for the predicted speedup or slowdown of the application's I/O on the target system relative to the reference system. We then use these ratios, as shown in equation 2, to predict the applications total I/O time on target systems. To calculate accuracy of our predictions, we run the application on the target systems and compare the predicted times with the actual time spent in I/O. We demonstrated the effectiveness of this method on spinning disks [4]. In this paper we extend our methodology to model patterns of I/O operations and use it to predict I/O time on a system with flash drives.

![](_page_1_Figure_1.png)

Figure 1. Methodology Overview.

For each I/O call i, target system x, calculate ratios as follows:

$$Ratio_{i,x}=\frac{\begin{array}{c}\mbox{\small{IOTime}}_{i,x}\\ \mbox{\small{IOTime}}_{i,references}\end{array}}{\begin{array}{c}\mbox{\small{IOTime}}_{i,x}\\ \mbox{\small{IOTime}}_{i,references}\end{array}}\tag{1}$$

For each target system x, calculate predicted total time spent in I/O as follows:

_PredictedTime${}_{\chi}=\sum_{i=0}^{n}$Ratio${}_{i,x}$* ApplicationTime${}_{i,reference}$ (2)

# III. WORKLOADS AND SYSTEMS

#### A. *Workloads*

€

1) *MADbench2*

MADbench2 is a benchmark that is derived from Microwave Anisotropy Dataset Computational Analysis Package (MADCAP) Cosmic Microwave Background(CMB) power spectrum estimation code [7]. CMB data is a snapshot of the universe 400,000 years after the big bang. MADbench2 retains the most computationally challenging aspect of MADCAP, to calculate the spectra from the skymap. MADbench2 retains the full complexity of computation, communication, and I/O, while removing the redundant details of MADCAP. The nature of the large calculations required for CMB data means that the large matrices used do not fit in memory, hence the benchmark uses an out-of-core algorithm. Each processor requires enough memory to fit five matrices at a given time. MADbench2 stores the matrices to disk when they are first calculated and reads them when required.

In our research MADbench2 was configured to run in synchronous I/O mode with concurrent readers/writers. We tested the application to run with 25 MPI tasks using POSIX and MPIIO APIs in separate runs. A total of 8 matrices of 7.2 GB size are used and stored in a single shared 57.6 GB file. These 8 matrices are distributed among the 25 MPI processes, and thus, each process works on 2.3 GB of data. The application makes I/O calls in three distinct phases, during phase 1 the matrices are written to disk, during phase 2 the matrices are read back and updated contents are written back to disk and finally in the last phase the matrices are read back from disk. Thus, each process issues a total of 16 reads/writes of size 288 MB.

#### 2) *Geological Imaging*

The second application we studied creates an image of a geological medium. The problem of imaging a geological medium is solved numerically by simulating the propagation of an acoustic wave front; additional details are in [5]. This application was implemented using multithreading based on the fork-join model. However, only the master thread issues file I/O and the remaining threads are not active. The application stores time-step data to disk and reads them back at later stage. The I/O is done in two distinct phases, during the first phase, 300 files of size 198MB are written to disk, and subsequently they are read back in reverse order of writing, i.e., the last one written is read back first. The application issues 189 0.74 MB, 117 0.42 MB, and 29 0.24 MB reads/writes to each file. Thus, reads/writes of size 0.74MB dominate the I/O time.

#### B. *Systems*

#### 1) *Dash with Flash – Target System*

In DASH system, flash drives are attached to batch nodes and I/O nodes. Each batch node is equipped with two Nehalem 2.4GHz quad-core processors and 48GB DDR3 memory. Intel X25-E 64GB flash drives is attached directly to the batch node. As for the I/O nodes, they have the same processors and memories as the batch nodes but more flash drives. Specifically, 16 Intel X25-E 64GB, totally 1TB flash drives are installed on each I/O node and set up as a software RAID-0. XFS file system is used to manage the flash dives on DASH.

#### 2) *Dash with disk – Reference System*

In DASH system, Seagate Momentus 250GB 7200RPM spinning disks are attached locally to the batch nodes. Spinning disks are managed by the Ext3 file system. €

#### 3) *Jade – Reference System*

Jade is a Cray XT4 system and has a total of 2152 compute nodes. Each node runs Compute Node Linux (CNL) and has one quad-core AMD Opteron processor and 8 GB of main memory. All nodes are connected in a 3D torus using a HyperTransport link to a Cray Seastar2 engine. The system has a total of 379 TB fiber channel RAID disk space that is managed by a Lustre file system.

# IV. EXPERIMENTS AND RESULTS

#### A. *Workloads*

In this paper we predict disk I/O times of the geological imaging application on batch nodes with flash drives and MADbench2 on I/O nodes with flash drives. While reference systems used are as follows: (1) For the geological imaging application we use DASH with disk, and (2) For MADbench2 we use Jade.

We used IOR to simulate the I/O operations of MADbench2 and report the results in the next section. We also used IOR to simulate I/O operations of the geological imaging application, however, due to high errors and due to lack of flexibility provided by IOR, we created our own IO benchmark. This IO benchmark was written to execute all reads/writes in the same pattern as the application. Additionally, we measured time spent by the application between consecutive IO calls and inserted those delays in our benchmark. Although we do not prove it, it is our hypothesis that for small size IO calls, the performance of our flash drive is worse for consecutive IO calls without delays as compared to with delays; the delay may give time for the flash drive to reach steady state.

#### B. *Results*

Ratios and predictions were calculated using equations 1 and 2 respectively. Since wall clock time of an application may differ from run to run, each application was executed five times on the machine and an average run time was used in these two equations. Thus, the average run times of I/O micro benchmark was used to predict run times of the applications under study. To calculate the prediction error, the predicted time is compared against the average run time of five executions of the applications under study. Accuracy for each target application x is calculated using Equation 3.

#### *PredictionErrorx* =100 * *PredictedTimex* − *ActualTimex* (3)

# *ActualTimex*

In equation 3, a negative value indicates that actual I/O time was greater than the predicted time, and a positive value indicates that the actual I/O time was less than the predicted time. For MADbench2 the prediction errors are as follows:

- POSIX API: -20.66%, -8.59%, and -14.79% for reads, writes, and total I/O time respectively
- MPIIO API: -19.92%, -14.76%, and -17.50% for reads, writes, and total I/O time respectively

For the geological imaging application, first using IOR we got error rates of 227% for total I/O. Next using our own IO benchmark we were able to reduce this error to 144% for total I/O. In particular, we noticed an improvement of total read error of 48% as compared to 800% using IOR. Furthermore, our lowest prediction error is 9% for the largest read, i.e., of size 0.74MB. While these results are encouraging, we need to continue to work on our benchmark and investigate other factors to accurately model this application.

# V. CONCLUSIONS AND FUTURE WORK

In this paper we presented a methodology to predict disk I/O time on a system with flash drives. Our method used a configurable I/O benchmark to measure speedup ratios of each I/O operation of an application and used them to predict an applications total I/O time. Our evaluation showed that for large size IO calls reasonable accuracy may be obtained by using this simple model and in the best case our prediction error is only 8.59%.

However, for applications that issue small size IO calls, the problem is more difficult. Additional parameters beyond those presented by IOR are required to get reasonable prediction errors. Towards this goal, we created our own IO benchmark that simulated the access pattern of the application as well as the delays between two consecutive calls. Our effort thus far reduced errors for one particular read size to 9%. However our error for total I/O is very high at 144%. To further improve our predictions, we are investigating other parameters such as File caching, Contention, and Synchronization delays. File caching is the ability to cache files in the memory subsystem; file caching can significantly speed up disk I/O. Contention affects the share of I/O resources that each application receives and thus is important to model. Finally, synchronization delays reflect how barrier synchronization and other data dependencies in the application change the rate at which I/O calls are made.

# VI. RELATED WORK

Related work has pursued I/O modeling and prediction by using script based benchmarks to replay an applications causal I/O behavior [10, 11] or using parameterized I/O benchmarks [12] to predict run time on the target system. Our modeling approach differs from the related work by using parameterized benchmarks to compute *speedup ratios* on target systems for each call and use that to predict an applications I/O time.

Pianola [10] is a script based I/O benchmark that captures causal information of I/O calls made by a sequential application. The information is captured by a binary instrumenter that, for each call, captures wall clock time of the call, the time spent servicing the call, and arguments passed to the call. Using this information a script is constructed which has sufficient information to replay an applications' I/O calls and time between two successive calls. Additionally, the script is also augmented to simulate the memory used by an application between calls. A replay engine can then use this script to replay an applications I/O behavior on any platform.

Like Pianola, TRACE [11] is a script-based I/O benchmark that simulates an I/O behavior of an application using causal information about the I/O calls. Unlike Pianola, TRACE used interposed I/O calls to capture information regarding I/O calls. TRACE is targeted for parallel applications and hence captures I/O events for each parallel task. In addition to I/O events, for each task, TRACE also includes information related to synchronization delays and computation time. Using this information a replayer simulates the I/O characteristic of each task of the original application.

In [12] IOR was used to simulate the I/O behavior of HPC applications. In this research an applications I/O behavior is first obtained by code and algorithm analysis and this information is then used to prepare inputs for the IOR benchmark. Next, IOR is then run on the target system to predict the *actual* I/O time of an application. Unlike in [12] we use IOR to capture speed up ratios for prediction.

# ACKNOWLEDGMENT

This work was supported in part by the DOD High Performance Computing Modernization Program, and by National Science Foundation under NSF OCI award #0951583 entitled "I/O Modeling EAGER", and by NSF OCI #0910847 entitled "Gordon: A Data Intensive Supercomputer", and by NSF OCI #0721397 entitled "Integrated Performance Monitor".

checkpoints on next-generation systems. In *24th IEEE Conference on Mass Storage Systems and Technologies* (MSST 2007), 2007.

- [2] IOR http://sourceforge.net/projects/ior-sio/
- [3] Laurenzano, M. A., Tikir, M. M., Carrington, L. C., Snavely, A. PEBIL: Efficient static binary instrumentation for Linux. In *proceedings of the IEEE Symposium on Performance Analysis of Systems and Software*. March 2010, White Plains, NY.
- [4] Meswani M. R., Laurenzano M. A., Carrington L., and Snavely A. Modeling and predicting disk I/O time of HPC applications. In *proceedings of 2010 User Group Conference (UGC 2010)*, Schaumburg, Il, Jun 2010
- [5] Wolfe, J. P. and Hauser, M. R. Acoustic wavefront imaging, Annalen der Physik, 507: 99–126, 1995.
- [6] Borrill, J., Oliker, L., Shalf, J., Shan, H., and Uselton, A. HPC global file system performance analysis using a scientificapplication derived benchmark. In *Parallel Computing,* 35, 6, 358-373, 2009.
- [7] Borrill, J. MADCAP: The microwave anisotropy dataset computational analysis package. In *Fifth European SGI/Cray MPP Workshop*, 1999.
- [8] Norman, M., and Snavely, A. Accelerating data-intensive science with Gordon and Dash. In *proceedings of the 2010 Teragrid Conference (TG '10)*, Pittsburgh, Pennsylvania, August 02 - 05, 2010.
- [9] He, J., Jagatheesan, A., Gupta, S., Bennett, J., and Snavely, A. DASH: a recipe for a flash-based data intensive supercomputer. In *proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis* (SC'10), New Orleans, Louisiana, November 13-19, 2010.
- [10] May, J. Pianola: A script-based i/o benchmark. In *Proceedings of the 2008 ACM Petascale Data Storage Workshop (PDSW 08)*, November 2008.
- [11] Mesnier, M. P., Wachs, M., Sambasivan, R. R., Lopez, J., Hendricks, J., Ganger, G. R., and O'Hallaron, D. Trace: Parallel Trace Replay with Approximate Causal Events. In *Proceedings of the 5th USENIX Conference on File and Storage Technologies*, February 2007.
- [12] Shan, H., Antypas, K., and Shalf, J. Characterizing and predicting the I/O performance of HPC applications using a parameterized synthetic benchmark. In *Proceedings of the 2008 ACM/IEEE Conference on Supercomputing* (SC), 2008.
- [13] He, J., Bennett, J., and Snavely, A. DASH-IO: an empirical study of flash-based IO for HPC. In *Proceedings of the 2010 Teragrid Conference* (TG'10) Pittsburgh, Pennsylvania, August 02 - 05, 2010.

# REFERENCES

- [1] Oldfield, R. A., Arunagiri, S., Teller, P. J., Seelam, S., Varela, M. R., Riesen, R., Roth, P. C. Modeling the impact of
