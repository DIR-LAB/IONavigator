# Improving the I/O Performance of Applications with Predictive Modeling based Auto-tuning

Ays¸e Bagbaba, Xuan Wang, Christoph Niethammer, Jos ˘ e Gracia ´

The High-Performance Computing Center Stuttgart (HLRS), University of Stuttgart

Stuttgart, Germany

Email: bagbaba@hlrs.de, xuan.wang.51@gmail.com, niethammer@hlrs.de, gracia@hlrs.de

11

2021 International Conference on Engineering and Emerging Technologies (ICEET) | 9

*Abstract*—Parallel I/O is an essential part of scientific applications running on high performance computing systems. Typically, parallel I/O stacks offer many parameters that need to be tuned to achieve the best possible I/O performance. Unfortunately, there is no default best configuration of parameters; in practice, these differ not only between systems but often also from one application use-case to the other. However, scientific users often do not have the time nor the experience to explore the parameter space sensibly and choose the proper configuration for each application use-case. This paper proposes an auto-tuning approach based on I/O monitoring and predictive modeling, which can find a good set of I/O parameter values on a given system and application use-case. We demonstrate the feasibility to auto-tune parameters related to the Lustre file system and the MPI-IO ROMIO library transparently to the user. In particular, the model predicts for a given I/O pattern the best configuration from a history of I/O usages. We have validated the model with two I/O benchmarks, namely IOR and MPI-Tile-IO, and a real Molecular Dynamics code, namely ls1 Mardyn. We achieve an increase of I/O bandwidth by a factor of up to 18 over the default parameters for collective I/O in the IOR and a factor of up to 5 for the non-contiguous I/O in the MPI-Tile-IO. Finally, we obtain an improvement of check-point writing time over the default parameters of up to 32 in ls1 Mardyn.

*Index Terms*—Parallel I/O; Auto-tuning; Predictive Modeling; Machine Learning; MPI-IO

### I. INTRODUCTION

Data-intensive scientific applications running on high performance computing (HPC) systems are correspondingly bottlenecked by the time it takes to perform input and output (I/O) of data from/to the file system. Some applications spend most of their total execution times in I/O [1]. This causes a huge slowdown and wastage of useful compute resources [2]. Thus, I/O becomes probably the most limiting factor for HPC applications [3]. A parallel I/O stack offers many optimizations that can help in improving the performance of I/O. However, understanding the I/O activity of an application and achieving efficient parallel I/O are challenging tasks due to the complex inter-dependencies between the layers of the I/O stack [4].

Figure 1 indicates a typical parallel I/O stack of many current HPC systems that is in order of user application, highlevel I/O library, Message Passing Interface I/O (MPI-IO), Portable Operating System Interface (POSIX-I/O), parallel file system, and storage system.

Each layer of the parallel I/O stack offers a set of tunable parameters to improve I/O performance, such as Lustre file system stripe size and count, whether or not to perform

![](_page_0_Figure_13.png)

Fig. 1: Typical I/O Stack of an HPC System.

collective I/O, a number of data aggregators for collective I/O, etc. [5]. The configuration of these parameters depends on diverse factors such as the I/O application, storage hardware, problem size, and concurrency [2]. For example, choosing a larger stripe size and stripe count in the Lustre file system is usually recommended. However, for a small data transfer size (32 KB), the writing performance of striping over 4 OSTs with 1 MB stripe unit was about %55 better than the performance of striping over 16 OSTs with 16 MB stripe unit.

When a configuration space gets larger, it becomes difficult to monitor the interactions between configuration options. Users who are not experts on parallel file systems might have no time or experience for tuning their applications to the optimal level. Sometimes they might even drop down the I/O performance by mistake [6]. Application developers work on application code optimizations rather than I/O optimization [2]. In most cases, the default settings are used, often leading to poor I/O efficiency [5]. As the complexity of large-scale applications and HPC systems increases, this brings more challenges in achieving high-performance I/O due to the lack of global optimizations. Available I/O profiling tools can not tell the optimal system default setups by easily monitoring and analyzing application [6]. Identifying sources of I/O performance bottlenecks requires a multi-layer view of the I/O activity. These issues make it increasingly difficult for users to find out the best configuration setting for their applications.

Auto-tuning can help users by automatically tuning I/O parameters at various layers [7]. There are many auto-tuning

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 22:49:51 UTC from IEEE Xplore. Restrictions apply.

works to improve I/O performance based on approaches such as heuristic search, analytical models, empirical models, etc. However, some of these approaches are time-consuming and not applicable. There is still a need for new studies that can efficiently save core hours and improve the I/O performance of applications. We propose predictive modeling based I/O autotuning system that can hide the complexity of the I/O stack from users and auto-tune a set of parameter values for an application on a given system to improve the I/O performance of parallel applications.

Our auto-tuning approach monitors I/O applications, constructs an I/O performance prediction model using a random forest regression algorithm and tunes the model further by assessing dynamic run-time results of the top configurations. This approach determines the good set of parameter values by using predicted values by this model rather than executing the application trial. This study makes the following contributions:

- It monitors I/O applications and saves the I/O related information.
- It develops predictive modeling based I/O auto-tuning approach that can hide the complexity of multiple I/O stack layers from users and improve I/O performance.
- It builds an I/O performance prediction model to extract expert knowledge from observations automatically.
- It uses the model to reduce the search space for good configurations and save core hours.
- It considers the dynamic run-time conditions of a parallel I/O system.
- It evaluates and demonstrates the proposed approach with two synthetic benchmarks and a real application.

The remainder of this paper is organized as follows: Section II gives related work regarding I/O research that motivates this work. Section III describes the general auto-tuning approach which we propose for solving HPC I/O tuning problems. All the experimental setup and results are presented in Section IV. Section V concludes the paper and discusses some possible future research directions.

## II. RELATED WORK

Among various optimizing potentialities, the I/O request is one of the most requested parts. Many approaches exist to determine good configuration parameters in a large search space through auto-tuning to improve the I/O performance of scientific applications.

Behzad et al. implemented a genetic algorithm based on I/O auto-tuning to traverse the search space systematically [4], [8]. However, this approach is time-consuming and could not be applied to each application use-case due to application-specific parameter values. In [9] manual-tuning HDF5 applications was studied, but it is an unmanageable task for users and application developers. [10] implements a pattern-driven parallel I/O tuning for HDF5 applications to optimize the I/O performance of HDF5 applications. A solution based on MPI-IO could be more widely used and supports parallel HDF5. Megha et al. used Bayesian optimization and performance prediction for automatic tuning that gives 20% median prediction errors for most cases [2]. We propose a dynamic parallel I/O auto-tuning solution to find an optimal set of parameters in comparatively less time using predictive modeling. This solution is currently based on the MPI-IO ROMIO library and Lustre parallel file system.

## III. AUTO-TUNING PARALLEL I/O

In this section, we define our I/O monitoring module, performance prediction model, then we show our auto-tuning system that explores optimal I/O parameters by using predictions of the model in a few seconds.

## *A. IO Tracer: Monitoring I/O Applications*

The IO *Tracer* is implemented with *one process tracing* policy. The *rank 0* is responsible for collecting tracing results and storing them into its allocated local memory. Meanwhile, the other MPI processes stay idle after contributing to the duration of their I/O operations. As a result, all other MPI processes keep running while the rank 0 MPI process saves the tracing results into its local memory.

After tracing the MPI reading/writing operations, the IO *Tracer* saves the I/O related information, such as operations' duration, data transfer sizes, operation bandwidths, names of MPI-IO subroutines, MPI info objects, and so on into the allocated memory. As soon as the application calls the MPI FINALIZE subroutine, the *rank 0* MPI process writes all tracing results into the log file and finalizes the IO *Tracer*.

# *B. IO Predictor: I/O Performance Predictive Modeling*

A modeling approach is considered that can model the I/O performance (e.g., I/O bandwidth) in terms of the parallel I/O stack characteristics. The performance model can be formally used to define the I/O performance of an application as follows:

$$\phi=f(\alpha,\zeta,\omega),\qquad\qquad\qquad(1)$$

Where α represents a set of observable parameters that describe application characteristics (problem size, I/O pattern, number of cores, etc.), ζ represents a set of observable parameters that describe file system and/or MPI-IO characteristics (Lustre parameters, MPI-IO hints, etc.), ω represents uncontrolled non-observable parameters, and φ represents I/O bandwidth. We aim to understand the relationship between φ and the parameters (α, ζ). For a given set of input parameter values in (α, ζ), the function f should give a prediction.

We collected a training data set with our monitoring module IO *Tracer* from runs in multiple problem sizes. On this training data set, we applied a non-linear regression method and constructed a predictive performance model. Remarkably, the random forest regression model gave successful prediction results for such a non-linear relationship between parameters. We call the model IO *Predictor*. We use IO *Predictor* to predict I/O performance for all possible combinations of tunable parameters. We then sort predictions and select the best-performing parameters for the given scale.

#### *C. Performance Prediction based Auto-tuning*

In auto-tuning, a na¨ıve strategy is to run an application using all possible combinations of tunable parameters to find the best. This becomes a highly time and resource-consuming approach depending on the size of the parameter space. Rather than this approach, we propose a predictive modeling based I/O auto-tuning system. Instead of running the application, we use predictions of IO *Predictor* (see Section III-2) as the objective function.

Figure 2 shows the overall architecture of I/O autotuning. We first collect training data for a variety of workloads/parameters by the IO *Tracer*, then we build a model IO *Predictor* in optimization module IO *Optimizer*. Then, we evaluate the model to get the best configuration. All possible combinations of tunable parameters are given to IO *Predictor* as input. It predicts the I/O performance of all these configuration sets by using a random forest regression method. Then, it sorts the predictions and selects the best-performing parameters among the measured performances for the given application and scale. The tuning module IO *Tuner* takes the best parameters suggested by IO *Predictor* and dynamically passes them to the MPI-IO routines of the application or benchmark in the PMPI wrapper. After executing I/O operations, performance results are used to refit IO *Predictor* with the dynamic conditions of a parallel I/O system adaptively.

![](_page_2_Figure_3.png)

Fig. 2: Overall architecture of I/O auto-tuning.

#### *D. Implementation*

The α parameters that we worked on are a number of cores (16-2400), problem size (256 B-64 MB), and I/O pattern (collective; individual), while the ζ configuration parameters include Lustre file system parameters; striping unit (1MB-32MB) and factor (1-16), MPI-IO parameters; whether or not to perform collective I/O (automatic; disable; enable) and number of data aggregators (1-16) as listed in Table I. [2], [6], [13] and [14] show that these parameters have

#### TABLE I: Training Set Configurations' Scope

| Name | Value |
| --- | --- |
| number of cores | 16 - 2400 |
| number of bytes | 256 B - 64 MB |
| number of aggregators | 1 - 16 |
| striping count | 1 - 16 |
| striping unit | 1 MB - 32MB |
| collective I/O | automatic; disable; enable |
| I/O pattern | collective, individual |

an important effect on the parallel I/O performance. The optimization criteria φ is the I/O bandwidth. Our modeling approach aims to understand the relationship between φ and the parameters (α, ζ). For a given set of input parameter values in (α, ζ), the function f should give a prediction. The ω parameters such as load on the file system by other processes are also potentially important but not easily observable; thus, these parameters have been ignored for simplicity in this study.

The random forest regression method was implemented in predictive modeling for such a non-linear relationship between parameters. It provides to extract knowledge from numerous decision trees instead of producing a single decision tree. Then, results are aggregated, so it can outperform any individual decision tree's output [15]. We selected maximum depth = 5, the number of estimators = 1000 in random forest method implementation and 80%-20% train-test data set split. The training set was not reused for the test set. A model was trained for each benchmark and application to predict write performance. 2153 instances for IOR, 164 instances for MPI-Tile-IO, 968 instances for ls1 Mardyn were used to train models. An instance includes parameters and the measured I/O bandwidth with these parameters in the training phase. Thus, the constructed IO *Predictor* model can predict I/O performance for an exhaustive set of all possible combinations of tunable parameters. IO *Predictor* model was extracted based on 100 iterations. While running the prototypical training process once for our search space consumed 40 hours wall time, time taken to build the model is about only 8.0 seconds(data-dependent).

#### IV. EXPERIMENTAL RESULTS

This section presents implementation results, I/O benchmarks and application used in this study, the supercomputer on which the experiments were conducted, and model evaluation.

#### *A. Benchmarks*

We chose two I/O benchmarks and a parallel I/O application to evaluate our approach: Interleaved or Random (IOR), MPI-Tile-IO, and ls1 Mardyn. These represent different I/O write motifs with different data sizes.

- IOR—I/O benchmark : IOR is one of the main HPC I/O benchmarks because it is highly configurable and contains different I/O interfaces. We have configured IOR in the range of 1 MB to 64 MB block sizes to collectively write in the shared files.
- MPI-Tile-IO : The MPI-Tile-IO benchmark tests the IOperformance in a real-world scenario. It tests how it

performs when it is challenged with a dense 2D data layout. We have configured MPI-Tile-IO number of tiles as much as a number of cores and in the range from 32 KB to 16184 KB element sizes.

- ls1 Mardyn [11]: ls1 Mardyn is a molecular dynamics (MD) simulation program which is optimized for massively parallel execution on supercomputing architectures. It is a highly scalable code. In this study, it is used for writing check-points. We have configured ls1 Mardyn in the range from 79655 molecules to 16802098 molecules.
## *B. System setup*

The experiments were conducted on the NEC Cluster platform (Vulcan) at HLRS (High Performance Computing Center Stuttgart). Vulcan consists of several front-end nodes for interactive access, and several compute nodes of different types for the execution of parallel programs. It has 761 nodes with a total of 24 cores, Centos 7 operating system, PBSPro Batch system, Infiniband + GigE node-node interconnect, 500 TB (Lustre) for Vulcan global disk [12], and the bandwidth is about 3 GB/sec. The Lustre file system consists of 54 OST storage targets, one RAID6 lun, 8+PQ, 2 TB disks.

The default setup of Lustre striping configuration on the experimental file system is striping factor=4 and striping unit=1048576. OpenMPI is from version 4.0.3.

#### *C. Results*

In this section, we show the results of our experiments for two benchmarks and application in different file sizes on Vulcan. The experiments have been repeated multiple times, and average values have been plotted.

Summary of performance improvements we have obtained for IOR benchmark is summarized in Figure 3, for MPI-Tile-IO benchmark in Figure 4, for ls1 Mardyn in Figure 5 at different scales. Note that only a subset of the combinations was run due to limited access to the platform.

Table II shows the I/O performances of the default and the optimized experiments for three use-cases are shown in Figure 3, Figure 4 and Figure 5. We also show the speedup that the auto-tuned settings achieved over the default settings for each experiment.

In all experiments, the optimized results were obtained by the best configuration promising the best performance predicted by IO *Predictor*. Using the model, we achieve an increase in I/O bandwidth of up to 18.9×over the default parameters for the IOR benchmark and 5.1×over the default parameters bandwidth for the MPI-Tile-IO benchmark. We got up to 32×improvements in ls1 Mardyn compared to the default performance. The optimal configurations of the most successful cases in our experimental results for the IOR benchmark, MPI-Tile-IO benchmark, and ls1 Mardyn are given in Table III.

As for validation of the performance model, 10-fold crossvalidation that average results for ten different splits is implemented to increase confidence in the model. IO *Predictor* can achieve 91.12% accuracy when using depth of the tree is

![](_page_3_Figure_11.png)

Fig. 3: Default vs. optimized write bandwidth on IOR for various transfer sizes running on 240 cores, 1200 cores, and 2400 cores of Vulcan. Y-axis represents I/O bandwidth in MBps and x-axis represents transfer sizes (in MB). The scales of the I/O bandwidth axes are different in the plots.

5. When the depth of the tree is increased, accuracy can be higher. However, it seems the model is subject to overfitting in this case. The model obtains less than 10% median prediction errors for most cases. A more comprehensive training data set can give better prediction results. Our future efforts will further explore more accurate model generations.

# V. CONCLUSION AND FUTURE WORK

In this study, we presented predictive modeling based I/O auto-tuning approach to monitor I/O applications and autotune the I/O parameters. We also presented a performance

![](_page_4_Figure_0.png)

Fig. 4: Default vs. optimized write bandwidth on MPI-Tile-IO for various transfer sizes running on 16 cores, 64 cores, and 256 cores of Vulcan. Y-axis represents I/O bandwidth in MBps and x-axis represents element sizes of core times core number of tiles (in KB). The scales of the I/O bandwidth axes are different in the plots.

model to estimate I/O performance based on the tracing files. It achieves improvements for write performance in I/O benchmarks and a real application on supercomputer Vulcan. Thereby, the training time to find the best parameters is drastically reduced from hours (application-dependent) for a na¨ıve strategy to only 8.0 seconds(data-dependent) on average. This is an enormous improvement in training time over past models for auto-tuning. We have validated our approach with two I/O benchmarks and a real application. We achieve an increase

![](_page_4_Figure_3.png)

Fig. 5: Default vs. optimized write I/O time on ls1 Mardyn for various transfer sizes running on 240 cores and 1200 cores of Vulcan. Y-axis represents I/O time in seconds and x-axis represents different numbers of molecules. Lower I/O time is better. The scales of the I/O time axes are different in the plots.

of I/O bandwidth by a factor of up to 18 over the default parameters for collective I/O in the IOR and a factor of up to 5 for the non-contiguous write in the MPI-Tile-IO. We obtain an improvement of check-point writing time over the default parameters of up to 32 in ls1 Mardyn. Thus, we demonstrate that our approach can indeed be helpful for I/O tuning of parallel applications in HPC. Our model can be trained with negligible effort for any benchmark or I/O application. This approach can be understood by users with little knowledge of parallel I/O without any post-processing step. It is implemented upon the MPI-IO library to be compatible with MPIbased engineering applications and be portable to different HPC platforms. As future work, the auto-tuning solution will be tested on applications in different professional areas to show usability.

#### ACKNOWLEDGMENT

The research leading to these results has received funding from the HPC-EUROPA3, 90043470.

#### REFERENCES

- [1] P. Carns, R. Latham, R. Ross, K. Iskra, S. Lang, and K. Riley, "24/7 Characterization of petascale I/O workloads", in 2009 IEEE International Conference on Cluster Computing and Workshops, 2009.

| Application |  |  | IOR (MB/s) |  |  | MPI-Tile-IO (MB/s) |  | ls1 Mardyn (s) |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #Cores |  | 240 | 1200 | 2400 | 16 | 64 | 256 | 240 | 1200 |
| Use case 1 | Default | 913.89 | 1659.64 | 1483.18 | 854.71 | 2400.53 | 7530.95 | 122.96 | 223.11 |
| Optimized |  | 1155.89 | 2440.42 | 3654.74 | 1012.69 | 3099.70 | 10078.97 | 22.93 | 61.97 |
|  | Speedup | 1.26 | 1.47 | 2.46 | 1.18 | 1.29 | 1.33 | 5.36 | 3.60 |
| Use case 2 | Default | 6238.56 | 6400.08 | 2849.65 | 875.50 | 1974.46 | 6138.91 | 1094.21 | 2344.46 |
| Optimized |  | 13067.73 | 25121.44 | 41475.43 | 989.94 | 2792.39 | 10384.21 | 67.00 | 109.27 |
|  | Speedup | 2.09 | 3.93 | 14.55 | 1.13 | 1.41 | 1.69 | 16.33 | 24.45 |
| Use case 3 | Default | 4645.64 | 6254.05 | 2162.98 | 726.43 | 1759.32 | 2122.02 | 1684.16 | 3714.91 |
| Optimized |  | 10866.29 | 36557.57 | 40980.18 | 783.73 | 2833.29 | 10771.1 | 51.95 | 126.47 |
|  | Speedup | 2.34 | 5.85 | 18.95 | 1.07 | 1.61 | 5.07 | 32.41 | 29.37 |

TABLE II: I/O Speedups of Applications with Optimized Parameters over Default Parameters.

| TABLE III: Found Some Optimal Configurations for IOR, MPI-Tile-IO and ls1 Mardyn |
| --- |

| Application | #Cores | striping factor | striping unit | collective I/O |
| --- | --- | --- | --- | --- |
| IOR | 240 | 4 | 4194304 | automatic |
|  | 1200 | 16 | 16777216 | disable |
|  | 2400 | 16 | 16777216 | disable |
| MPI-Tile-IO | 16 | 4 | 4194304 | automatic |
|  | 64 | 16 | 1048576 | disable |
|  | 256 | 16 | 4194304 | disable |
| ls1 Mardyn | 240 | 16 | 1048576 | automatic |
|  | 1200 | 16 | 1048576 | automatic |

- [2] M. Agarwal, D. Singhvi, P. Malakar and S. Byna, "Active Learningbased Automatic Tuning and Prediction of Parallel I/O Performance", 2019 IEEE/ACM Fourth International Parallel Data Systems Workshop (PDSW), Denver, CO, USA, 2019, pp. 20-29.
- [3] H. Luu, M. Winslett, W. Gropp, R. Ross, P. Carns, K. Harms, M. Prabhat,S. Byna, and Y. Yao, "A Multiplatform Study of I/O Behavior on Petascale Supercomputers", in Proceedings of the International Symposium on High-Performance Parallel and Distributed Computing, 2015, pp. 33–44.
- [4] B. Behzad, S. Byna, Prabhat, and M. Snir: Optimizing I/O Performance of HPC Applications with Autotuning. ACM Trans. Parallel Comput. 5, 4, Article 15, 27 pages, (2019).
- [5] B. Behzad, S. Byna, S. M. Wild, M. Prabhat, and M. Snir, "Improving parallel I/O autotuning with performance modeling", in 23rd International Symposium on High-Performance Parallel and DistributedComputing. ACM, 2014, pp. 253–256.
- [6] X. Wang, (2017). A light weighted semi-automatically I/O-tuning solution for engineering applications (Doctoral dissertation). Retrieved from OPUS - Publication Server of the University of Stuttgart, http://dx.doi.org/10.18419/opus-9763.
- [7] P. Balaprakash, J. Dongarra, T. Gamblin, M. Hall, J. K. Hollingsworth,B. Norris, and R. Vuduc, "Autotuning in High-Performance Computing Applications", Proceedings of the IEEE, vol. 106, no. 11, 2018.
- [8] B. Behzad, H. V. T. Luu, J. Huchette, S. Byna, R. Aydt, Q. Koziol,M. Sniret al., "Taming parallel I/O complexity with auto-tuning", in Proceedings of the International Conference on High Performance Computing, Networking, Storage and Analysis. ACM, 2013, p. 68.
- [9] M. Howison, , Q. Koziol, D. Knaak, J. Mainzer, and J. Shalf, "Tuning HDF5 for Lustre file systems", 2010.
- [10] B. Behzad, S. Byna, Prabhat, and M. Snir, "Pattern-driven Parallel I/O Tuning", in Proceedings of the 10th Parallel Data Storage Workshop, ser. PDSW '15, Austin, Texas: ACM, 2015, pp. 43–48, ISBN: 978-1- 4503-4008-3. DOI: 10.1145/2834976 . 2834977. [Online]. Available: http : / / doi . acm . org / 10.
- [11] ls1 mardyn: The Massively Parallel Molecular Dynamics Code for Large Systems C. Niethammer, S. Becker, M. Bernreuther, M. Buchholz, W. Eckhardt, A. Heinecke, S. Werth, H. Bungartz, C. W. Glass, H. Hasse, J. Vrabec, and M. Horsch, Journal of Chemical Theory and Computation 2014, 10 (10), 4455-4464.
- [12] The NEC Cluster (Vulcan), https://kb.hlrs.de/platforms/index.php/ Vulcan. Last accessed 1 Feb 2021.

- [13] F. Isaila, P. Balaprakash, S. M. Wild, D. Kimpe, R. Latham, R. Ross,and P. Hovland, "Collective I/O tuning using analytical and machine learning models", in International Conference on Cluster Computing. IEEE, 2015, pp. 128–137.
- [14] S. Madireddy, "Machine Learning Based Parallel I/O Predictive Modeling: A Case Study on Lustre File Systems", in: ISC'18: International Conference on High Performance Computing, 2018.
- [15] S. Benedict, R. S. Rejitha, P. Gschwandtner, R. Prodan and T. Fahringer, "Energy Prediction of OpenMP Applications Using Random Forest Modeling Approach", 2015 IEEE International Parallel and Distributed Processing Symposium Workshop, Hyderabad, 2015, pp. 1251-1260.

