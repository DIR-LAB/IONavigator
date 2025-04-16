# Performance Prediction of HPC Applications on Intel Processors

Carlos Rosales, Antonio Gomez-Iglesias, Si Liu, Feng Chen, Lei Huang, ´ Hang Liu, Antia Lamas-Linares, John Cazes Texas Advanced Computing Center The University of Texas at Austin Austin, Texas

Email: {carlos,agomez,siliu,chenk,huang,hliu,alamas,cazes}@tacc.utexas.edu

*Abstract*—It is commonly the case that a small number of widely used applications make up a large fraction of the workload of HPC centers. Predicting the performance of important applications running on specific processors enables HPC centers to design best performing system configurations and to insure good performance for the most popular applications on new systems. In the analyses presented in this paper we use applications that are widely used on current open science HPC systems. We characterize the performance of these applications across a spectrum of modern processors and then create a mathematical model to predict their behavior on possible future processors. The hardware sensitivity studies required to build the predictive model are carried out in an HPC cloud resource with bare metal access, and we describe the process and advantages of this approach in detail.We define and discuss the mathematical model that we have designed and compare the predicted performance of these codes with the empirical results obtained in different chips. Finally, we also use the model to estimate the efficiency of future chips. The results indicate that the model is able to estimate the performance of these codes with a relatively small error across a fairly wide spectrum of chips.

*Index Terms*—performance; HPC; scalability; prediction; Xeon;

#### I. INTRODUCTION

Characterizing the performance of High Performance Computing (HPC) applications is critical for understanding how they perform on different systems. While the number of applications that users run on these systems is very broad, a large fraction of the resources of an HPC system are normally used by a handful of applications. The Texas Advanced Computing Center (TACC) hosts one of the most powerful open science systems in the world, Stampede. Information on the applications which execute on Stampede is routinely collected [1]. From that data, we extracted that only 10 applications consume nearly 50% of the execution resources on Stampede.

With the ever-growing need for more computational resources, HPC centers are continuously upgrading or installing new systems. The hardware available for configuring these systems is also in constant evolution. It is important for HPC centers to be able to design systems that satisfy the requirements of a large fraction of their existing and potential users. However, these systems are often designed well before the hardware is commercially available. This makes it difficult to predict the performance of future system configurations. We focus on being able to characterize the performance of the most popular scientific applications on a single node. This will help us to make informed decisions on future acquisitions as well as help other groups that face similar challenges.

As mentioned, typically a relatively small number of applications represent a large fraction of both the number of jobs and number of computing hours consumed in HPC centers. For this work we have selected four of the ten most representative applications that run on the Stampede system. These applications are NAMD [2], GROMACS [3], WRF [4] and Quantum ESPRESSO [5]. Other applications among the most consuming in terms of computing time were codes used by a single user or a very small number of users. However, these are production codes with a vast number of users and which are under continuous development. They have been widely analyzed and optimized for many different architectures and networks.

However, identifying the most popular applications and understanding how they work on a given processor is not sufficient to reach the goal of predicting their performance on future node hardware configurations. In this paper we present a mathematical model that allows us to estimate the performance of these codes in a variety of processors. As previously mentioned, we focus on the single node performance of these codes. We ignore the impact of the network or I/O on our experiments. When focusing on the single node performance two main elements need to be taken into account: CPU and memory. Each processor presents different characteristics for these two elements. While CPU frequency is normally the most obvious characteristic, it is also important to consider other internal elements of modern processors like vector units, branch prediction, out of order execution, or the number of stages in the instruction pipeline. Regarding memory, while many elements can not be fully understood because of the limited information available (i.e. cache replacing algorithms, prefetching, and so on), it is still possible to study the impact of changes in frequency and overall bandwidth in the performance of these codes.

It is the authors' hope that the procedures described in this work will become a key milestone in the process of designing and acquiring new HPC systems. The techniques described here can be used to determine overall impact of system balance and design on the known dominant applications used in a system. Embedding a clear and quantitative evaluation of design decision effects on true system throughput - as judged by the applications most executed by users rather than synthetic benchmarks - will benefit all areas of science that use HPC resources.

The rest of the paper is organized as follows: Section II presents the related work; in Section III we describe the applications that we have used as well as the use cases considered, whereas Section IV introduces the mathematical model that we have built to estimate the performance of these applications. Section V details the computational environment used for these tests, and the results of applying the model to different processors are detailed in Section VI. Finally, Section VII summarizes the paper and presents some future work.

#### II. RELATED WORK

The literature on application characterization in HPC is extensive, but changes in the performance properties of computer hardware as well as in the properties of the applications make many of the specific analyses and conclusions unreliable or irrelevant within a few years.

In [6] authors present a framework for predicting the performance of applications on HPC environments. While it presents similarities with the current work, it did not provide a good understanding of the most typical codes that run in these computational resources. A second paper uses the framework to study full codes [7] but these studies are over ten years old and have not been recently updated.

Similarly, in [8] authors present a comprehensive framework that even supports GPUs. However, the paper focuses on popular miniapps instead of common production codes that are typically used on modern HPC environments.

Predicting the performance of scientific applications was also the focus of [9]. However, in that work the authors focused on large-scale performance, which considers the network. We only target the intra-node performance in this paper, since HPC users tend to run their applications at scales where the parallel efficiency is high and the overall performance is not dominated by network effects. It is also a way to establish the validity of our model which could be extended to include network effects at a later date.

Authors in [10] and [11] present a model that shares some ideas with our current study. However, the authors simply focus on the characteristics of the CPU, ignoring key elements in the performance of multi- and many-core chips like memory. Those studies can be useful, however, for studying the performance of a single core or serial codes.

In [12], authors present an overview of how to model the performance of applications in multicore chips. The level of detail that it requires would not be interesting in our study due to the several changes in the hardware processors that lead to different performance for parallel applications. It is also focused on the characteristics of the CPU, ignoring other elements in modern chips that impact the performance of the applications.

It is possible to find several articles that focus on the performance of specific components of HPC systems [13] or even cloud-based systems [14]. These studies do not consider the most typical scientific applications. Moreover, authors do not tackle the most challenging elements in those studies, like forecasting performance on chips that are not still in the market.

An important characteristic of this work is that we consider full production codes instead of benchmarks or miniapplications. Even carefully designed mini-apps can have significant deviations from the behavior of the full application. For example, [15] shows that the NEKBONE mini-app displays a 5:1 ratio of DRAM reads to writes on the tested system, while the full NEK application shows a 3:1 ratio of DRAM reads to writes on the same system, and that the two codes have significantly different address re-use distances, and significantly different communication topologies.

For the larger scientific community, there is good coverage of applications that are also of interest to the major government agencies, but much less information available outside of those areas. Authors in [16] review the performance scaling of NAMD, MILC, and DNS, with an emphasis on MPI communication patterns, using the Intrepid, Ranger, and Jaguar systems (now all out of production). Other efforts like [17] compare the performance of the NSF application benchmarks WRF, MILC, PARATEC, and HOMME on three SGI Altix platforms, with different processor versions and interconnect versions and configurations. Analysis was limited to execution-time scaling, and performance counters were limited to floating-point operation counts.

There are few published studies using hardware sensitivity analysis to determine whole-program performance characteristics in HPC. A recent example is [18], which uses hotspot instrumentation and a machine learning system to predict the performance of applications under the effect of reduced DRAM bandwidth (controlled by BIOS modification of DDR3 DRAM frequency on a commodity server platform). A disadvantage of the machine learning approach is that the results are not available to the user in terms that correspond to the physical properties of the system.

Other sensitivity analyses [7], [19] compute the sensitivities using previously developed detailed performance models, rather than directly measuring the sensitivity by varying the performance parameters of the system. While this is an appropriate use of a performance model, the abstractions and approximations inherent in creating the performance model reduce the accuracy of the sensitivity estimates, and we argue that with current hardware there are many sensitivity experiments that can be done directly.

Foundations of this work can be found in a 2007 presentation [20]. A number of differences between applications and benchmarks were discussed, but the specific information is almost entirely out of date and deserves revisiting.

## III. SELECTED APPLICATIONS

As already introduced, we have selected some of the most representative applications that users run on the Stampede cluster.

## *A. NAMD*

NAMD [2] is a parallel molecular dynamics code for highperformance simulation of large molecular systems used by many research teams around the world and the 2002 Gordon Bell Prize winner. NAMD is also the most used application on Stampede. This study uses the APOA1 NAMD benchmark with modified input. The APOA1 benchmark is a 92-thousand atom molecular dynamics simulation of Apolipoprotein A-1 which is the primary component of the high-density lipoprotein cholesterol molecule. Multicore version of Charm++ 6.7.1 and NAMD 2.11 were built for the benchmark on a single node.

#### *B. WRF*

The Weather Research and Forecasting (WRF) Model [4] is a widely used numerical weather prediction system used for both research and operational forecasts. WRF is primarily a Fortran code implemented using MPI and OpenMP for distributed computing. The problem space on each process is divided into tiles that are processed by OpenMP threads. Ideally, the best performance is achieved when the size of the tile fits into the smallest cache. Having multiple application tiles allows WRF to obtain high levels of memory bandwidth utilization. A substantial effort was made to optimize WRF for the first generation Xeon Phi, Knights Corner [21]. The current version of WRF, 3.7.1, supports a configuration option for the KNC. For this investigation the benchmark case is a 12km simulation over the Continental U.S. (CONUS) domain on October 24, 2001 with a time step of 72 seconds.

## *C. Quantum ESPRESSO*

Quantum Espresso (QE) [5] is an integrated suite of Opensource codes for electronic-structure calculations and materials modeling at the nanoscale. It is based on density-functional theory, plane waves, and pseudopotentials. For our experiments, we have chosen a medium size benchmark input for PWscf, AUSURF112. We use Quantum Espresso V5.4.0.

## *D. GROMACS*

GROMACS is a versatile package to perform molecular dynamics, i.e. simulate the Newtonian equations of motion for systems with hundreds to millions of particles [3]. It is primarily designed for biochemical molecules like proteins, lipids and nucleic acids that have a lot of complicated bonded interactions. In this study, Hen egg white lysozyme (PDB code 1AKI) and water (SPC model) solutions were simulated using version 2016 RC. The simulated systems consist a total of 140124 atoms. All simulations were performed in the isothermal isobaric (NpT) ensemble at 300 K and 1 atm. This code uses intrinsincs to implement the vectorization of the most time consuming kernels. It is possible to disable the intrinsics at compile time.

## IV. APPLICATION PERFORMANCE MODEL

In order to model and predict the performance of the varied set of applications selected we chose to follow the sensitivity analysis methodology proposed by John D. McCalpin [20]. Following this methodology we assume a model where the time taken by an application to complete a given workload is divided into two contributions: i) a contribution which depends exclusively on the floating point throughput of the processor; ii) and a contribution that depends exclusively on the memory bandwidth of the processor. These contributions are considered as independent and non-overlapping.

Equation 1 shows the proposed model. The terms Rcpu and Rbw represent the floating point processing rate and the transfer rate to main memory (bandwidth) respectively. These two values can be determined directly from the processor characteristics. The terms Wcpu and Wbw are the amount of work the application requires from the CPU and the memory subsystem respectively. We find these two values via least squares fitting of a large set of controlled application execution tests.

$$T=\frac{W_{cpu}}{R_{cpu}}+\frac{W_{bw}}{R_{bw}}\tag{1}$$

The model is simple and may not provide a prediction as accurate as others based on detailed application instrumentation. However, it has two clear advantages: i) it provides clear insight on the application characteristics; ii) it does not require a complex instrumentation and analysis framework. We expect to expand the model to include additional terms for IO, latency, and network in the future, but the two terms selected for the current work have been shown to have the ability to predict performance for multiple scientific workloads [20]. An important characteristic of this model is that it presents correct asymptotic behavior as CPU rate and memory transfer rate go to zero for infinity limits.

While Rcpu and Rbw can be easily obtained, we need to collect several data necessary to calculate terms Wcpu and Wbw. In order to attain this data, we first selected an existing processor to run the target codes. We chose Intel Xeon E5- 2670 v3 (Haswell). This processor provides two 256 bit vector units. Then we performed multiple runs with each application at fixed processor speeds between 1.2 and 2.6 GHz, and for each clock speed four different DRAM speeds are used: 1333, 1600, 1866, and 2133 MHz. The application times are performed setting the uncore clock to maximum frequency and the snoop mode to *Home Snoop* in all cases. Since Haswell processors are capable of maintaining an uncore frequency that is independent of the core clock speed this setup allows for a differentiation of the application sensitivity to floating point throughput and to memory bandwidth.

The bandwidth term Rbw is obtained by executing the STREAM benchmark [22] for each CPU and DRAM frequency and taking the value of the Triad kernel as the effective transfer rate. This gives us a modest, but useful, dynamic range from 77 GB/s to 115 GB/s when using all the physical cores of

![](_page_3_Figure_0.png)

![](_page_3_Figure_1.png)

Fig. 1. Results of STREAM on a single Haswell core at different CPU and DRAM frequencies

The floating point rate Rcpu for each application is obtained as described in Eq. 2, where frequency is the CPU clock frequency in GHz, cores is the number of cores, and vector is the effective vector utilization factor. The effective vector utilization factor is obtained by comparing execution times for a given application with different levels of vectorization as well as by disabling vectorization during compilation.

Rcpu = frequency × cores × vector (2)

Model fits were produced using the nonlinear least squares Levenberg-Marquardt algorithm [23]. All measurements and predictions were based on the results obtained when using all cores, as well as a single process per core. This process is more effective than basing the prediction on the single core performance because for most modern multicore processors and applications memory bandwidth is not exhausted for single core runs. The measurements included running the applications a number of times for each combination of CPU-Memory frequency. Results did not vary significantly between runs, and the average was used as input for the fitting process.

## V. USING A CLOUD-BASED SYSTEM

Performing sensitivity studies where CPU and DRAM frequencies must be changed is not something that can be typically done in production HPC systems by a regular user since it requires elevated permissions. We chose to use Chameleon [24] for our experiments. Chameleon is a cloud-based system designed to provide bare metal provisioning of hardware. This, effectively, allows users to have a higher access to different elements of the system than when using traditional clusters. Having a resource that provides the level of access to the hardware that Chameleon offers results in being able to configure our system as we need it. This also shows the potential of this system for research in different areas of computer science.

Since this is a cloud-based system, we selected CentOS 7 with Intel compiler version 16.0.2 and Intel MPI version 5.1.3 for our experiments. Once we decided the image that had to be deployed, we selected a number of physical hardware nodes to run the tests. We selected a set of dual socket nodes with Intel Haswell (E-2670 v3) processors with 24 cores per node and hyperthreading enabled. As described earlier, to build our performance model we needed to run the different codes at different CPU and memory speeds. Once the instances of our image were running we were able to connect to them, elevate permissions to root, and make the necessary changes in the configuration of each of the nodes. Configuration settings were changed remotely by using the Dell DRAC 1 tools on each of the nodes. In particular, the syscfg tool was used to modify some of the BIOS options that control the memory behavior. We also varied the CPU frequency using the Model-Specific Registers (MSR) on the processor.

Fig. 2 shows an overview of the system once the instances have been deployed. On top of the software required to operate the system, we select an image that has already been customized for this hardware. Then, we installed our own packages, created a snapshot of our own image, and deployed it.

![](_page_3_Figure_11.png)

Fig. 2. Overview of the runtime model in Chameleon

#### VI. MEASURED PERFORMANCE

Figures 3 through 6 summarize the results of the sensitivity studies for the codes of interest. As seen in the figures the performance of the molecular dynamics codes NAMD and GROMACS is dominated by processor frequency; these two applications show no significant dependence on memory bandwidth as it can be derived from the performance being almost identical for all memory frequencies. Quantum ESPRESSO shows a mild dependence on memory bandwidth, while WRF has a very strong dependence on memory bandwidth. Although the difference across curves corresponding to different DRAM frequencies may seem visually small, it is important to realize that the range of memory frequencies studied is much shorter

1http://www.dell.com/content/topics/global.aspx/power/en/ps2q02 bell

than the range of CPU frequencies. Thus, small absolute differences across DRAM curves correspond to substantial fractional changes with respect to the effective memory bandwidth.

![](_page_4_Figure_1.png)

Fig. 3. Measured performance of NAMD on an Intel Xeon E5-2670 v3 (Haswell)

![](_page_4_Figure_3.png)

Fig. 4. Measured performance of GROMACS on an Intel Xeon E5-2670 v3 (Haswell)

## *A. Sanity Tests*

As a sanity test, we performed a prediction for the performance that each application would have on a processor similar to the CPU previously used in to gather the data to build the model, but not of the same family. We opted to predict the application performance for the Sandy Bridge E5- 2680 v1 processors in Stampede. Each node in Stampede is a dual socket with two Sandy Bridge processors, with 16 cores per node. Since it is also a Xeon processor with two 256 bit vector units we expected to obtain results that would be not too far from the measured values. In this case the CPU rate was calculated as the measured clock speed during execution (measured with the perf stat command) and the number of cores in a node: Rcpu = 3.0×16 = 48. Memory bandwidth

![](_page_4_Figure_7.png)

Fig. 5. Measured performance of Quantum ESPRESSO on an Intel Xeon E5-2670 v3 (Haswell)

![](_page_4_Figure_9.png)

Fig. 6. Measured performance of WRF on an Intel Xeon E5-2670 v3 (Haswell)

was measured at 78 GB/s when all cores run STREAM, so Rbw = 78.

The results summarized in Table I show that our predictions were within 20% of the measured performance except in the case of Quantum ESPRESSO. After analyzing the results in detail we suspected the large deviation was due to the partitioning scheme used by the Plane Wave algorithm. This algorithm seemed to be more effective when using 24 cores rather than 16. Figure 7 shows the scalability of Quantum ESPRESSO, the plateau in performance that starts at 8 cores and goes beyond the 12 core count supports this hypothesis. For codes of this type, which present a non smooth scaling as the number of cores increases, more detailed scaling studies would be necessary in order to refine the prediction.

#### *B. Performance Prediction for KNL*

Our next step was to generate predictions for a completely different design, so that it would test whether our model was appropriate. We chose the Intel Knights Landing (KNL)

| TABLE I |
| --- |
| PREDICTED AND MEASURED PERFORMANCE OF THE CODES ON AN INTEL |
| XEON E5-2680 V1 (SANDY BRIDGE) |

| Application | Measured Time | Predicted Time | Relative Error (%) |
| --- | --- | --- | --- |
| NAMD | 0.32 | 0.28 | 12 |
| GROMACS | 71.3 | 58.5 | 18 |
| QE | 660.0 | 399.9 | 39 |
| WRF | 136.1 | 113.1 | 17 |

![](_page_5_Figure_2.png)

Fig. 7. Scalability of Quantum ESPRESSO on E5-2670 v3 (Haswell)

processor configured in Cache memory mode and Quadrant clustering mode [25]. The memory bandwidth in this mode was measured at 330 GB/s, so Rbw = 330. The CPU processing rate was Rcpu = 1.4×68 = 95.2 except in the case of WRF, which showed a high vector utilization fraction in our vector/no-vector tests, so for WRF we used the vector/novector execution time ratio (1.35) to modify the base Rcpu as described earlier: Rwrf cpu = 95.2×1.35 = 128.5. In addition to this, and given the large discrepancy in architectural features between the Intel Xeon processor and the Atom Silvermont based KNL processor we run an issue rate limited scalar code on a single core of the Chameleon Haswell processors and on a single core of a Silvermont processor (Celeron J1900 model). The results indicated that, once the performance was normalized by frequency, a Haswell core seems to provide nearly twice the throughput in scalar operations that a Silvermont processor. This is important because in its current form our model would not be capable of including this type of architectural difference. Including the measured architecture factor of 0.41 in the Rcpu term produced high fidelity predictions for KNL. As shown in Table II the error for all applications except NAMD remained below 10%, a welcome result when moving across significantly different architectures. We investigated NAMD further, and compiled a version using the -xAVX flags instead of the -xMIC-AVX512 flag we had used for Table II in order to achieve the best possible performance. The results were striking. Our model would predict the AVX performance on KNL with an error of only 3%. Given that only one of the vector units in KNL is

| Application | Measured Time | Predicted Time | Relative Error (%) |
| --- | --- | --- | --- |
| NAMD | 0.22 | 0.33 | 51.8 |
| NAMD (AVX) | 0.32 | 0.33 | 3.1 |
| GROMACS | 66.4 | 66.8 | 0.6 |
| QE | 420.0 | 381.4 | 8.4 |
| WRF | 51.1 | 46.3 | 9.5 |

#### TABLE III CHARACTERISTICS OF THE E5-2680 FAMILY

| E5-2680 v1 | E5-2680 v2 | E5-2680 v3 | E5-2680 v4 |
| --- | --- | --- | --- |
| Sandy Bridge | Ivy Bridge | Haswell | Broadwell |
| 8 cores | 10 cores | 12 cores | 14 cores |
| 2.7 GHz | 2.8 GHz | 2.5 GHz | 2.4 GHz |
| 51.2 GB/s | 59.7 GB/s | 68 GB/s | 76.8 GB/s |

capable of executing AVX instructions this seems to indicate that our model underestimates the utilization of the second VPU when the AVX512 ISA is used.

## *C. Performance Prediction for Future Xeon Processors*

Next, we wanted to use our model to forecast the performance of these applications on a future, fictional processor. We considered the current family of E5-2680 processors as seen in Table III. Following a linear fit it is possible to see that a good guess would indicate 16 cores for the next generation of processors. A conservative estimate for CPU frequency is 2.2 GHz. For memory bandwidth, we can see that the average bandwidth per core has remained close to 6 GB/s. Since we are supposing 16 cores, the bandwidth for this imaginary future processor would be 96 GB/s. We are not implying that this will be the next E5-2680 v5, that it will be part of the E5 family, or that there will be an E5- 2680 v5. Our imaginary processor is an extrapolation based on the capability trends of previous processors in the Xeon family. Since we assign a peak memory bandwidth of 96 GB/s per socket, we will define out Rbw value as 85% of the dual socket number. This is a commonly achieved fraction of peak on Haswell, measured with STREAM, and an improvement over Sandy Bridge that is due to core architecture changes and that we consider unlikely to disappear in future processors of the family. For a dual socket of this imaginary processor, we obtain Rbw = 96 × 2 × 0.85 = 163 GB/s following this rule. The CPU work rate is simply defined as the number of cores times the frequency Rcpu = 16 × 2 × 2.2 = 70.4 We continue adding a factor 1.35 to Rwrf cpu to account for its good vectorization characteristics.

Table III cites the memory bandwidth per socket for a Sandy Bridge processor as 51.2 GB/s, and this may seem to be in apparent contradiction with the stated 78 GB/s used to make performance predictions for the E5-2670 processors in Stampede in Section VI-A. The explanation is simple: 78 GB/s is the measured STREAM bandwidth for the Triad kernel, which is approximately 76% of the dual socket peak performance listed by the vendor (2×51.2=102.4 GB/s). It is always preferable to use measured values for this purpose because applications can only take advantage of the maximum sustained bandwidth of a processor, and not the absolute peak.

With our model, and the characteristics previously described, we obtained the results shown in Table IV. The projected improvements in performance were significant, with WRF achieving the highest projected improvement in performance when compared to current technology. This was expected, since we have built a future processor that has higher memory bandwidth and floating point output for vectorizable codes, but only a minor increase in scalar throughput. The projections were also conservative since all of these community codes experience improvements with each processor family.

#### VII. CONCLUSION

We have presented a performance forecast model that allows to predict the performance of HPC applications on different architectures. We have selected some of the most popular applications in HPC systems and performed detailed sensitivity analyses for a typical workload. The results of these analyses are then used in our forecast model to study how the applications will behave in other architectures. When compared to the empirical results, the predictions show good accuracy. This makes us confident in the validity and usefulness of the model as we extend our studies to future hardware and refine the model itself.

We have used a cloud-based system for our experiments. This system is designed to achieve the highest possible performance from the hardware and provides users with high levels of controls over the hardware configuration. Based on our experience, this type of system represents an optimal alternative for this type of research because of its flexibility, the simple provisioning of resources, and the cost effectiveness of the setup.

As future work we plan on continuing these studies to further explore other hardware, including non Intel processors. As we move forward we plan on identifying areas where the model that can be changed to improve forecast accuracy. This will require significant work in terms of identifying not only properties of the hardware that the model must contain because they are relevant to important community workloads, but also methodologies to incorporate them into the model. We also consider adding other elements that impact the performance of production codes in HPC systems like IO, latency, and network.

#### ACKNOWLEDGMENT

The authors gratefully acknowledge National Science Foundation support under award numbers ACI-1134872 (Stampede), ACI-1419141 (Chameleon) and ACI-10-53575 (XSEDE). We would also like to thank James C. Browne and John D. McCalpin for their invaluable input and Cody Hammock for his assistance with Chameleon setup.

## REFERENCES

- [1] K. Agrawal, M. R. Fahey, R. T. McLay, and D. James, "User environment tracking and problem detection with XALT," in *Proceedings of the First International Workshop on HPC User Support Tools, HUST '14, New Orleans, Louisiana, USA, November 16-21, 2014*, C. Bording and A. Georges, Eds. IEEE, 2014, pp. 32–40. [Online]. Available: http://dx.doi.org/10.1109/HUST.2014.6
- [2] J. C. Phillips, R. Braun, W. Wang, J. Gumbart, E. Tajkhorshid, E. Villa, C. Chipot, R. D. Skeel, L. Kal, and K. Schulten, "Scalable molecular dynamics with NAMD," *Journal of Computational Chemistry*, vol. 26, no. 16, pp. 1781–1802, 2005. [Online]. Available: http://dx.doi.org/10.1002/jcc.20289
- [3] H. Berendsen, D. van der Spoel, and R. van Drunen, "GROMACS: A message-passing parallel molecular dynamics implementation," *Computer Physics Communications*, vol. 91, no. 1, pp. 43 – 56, 1995. [Online]. Available: http://www.sciencedirect.com/science/article/pii/001046559500042E
- [4] W. C. S. et al., "A description of the advanced research WRF version 3," National Center for Atmospheric Research, Tech. Rep., 2008.
- [5] P. G. et al., "Quantum ESPRESSO: a modular and open-source software project for quantum simulations of materials," *Journal of Physics: Condensed Matter*, vol. 21, no. 39, p. 395502, 2009. [Online]. Available: http://stacks.iop.org/0953-8984/21/i=39/a=395502
- [6] A. Snavely, L. Carrington, N. Wolter, J. Labarta, R. Badia, and A. Purkayastha, "A framework for performance modeling and prediction," in *Supercomputing, ACM/IEEE 2002 Conference*, Nov 2002, pp. 21–21.
- [7] L. Carrington, X. Gao, N. Wolter, A. Snavely, and R. Campbell, "Performance sensitivity studies for strategic applications," in *Users Group Conference, 2005*, 2005, pp. 400–407.
- [8] S. Lee, J. S. Meredith, and J. S. Vetter, "COMPASS: A framework for automated performance modeling and prediction," in *Proceedings of the 29th ACM on International Conference on Supercomputing*, ser. ICS '15. New York, NY, USA: ACM, 2015, pp. 405–414. [Online]. Available: http://doi.acm.org/10.1145/2751205.2751220
- [9] R. Susukita, H. Ando, M. Aoyagi, H. Honda, Y. Inadomi, K. Inoue, S. Ishizuki, Y. Kimura, H. Komatsu, M. Kurokawa, K. J. Murakami, H. Shibamura, S. Yamamura, and Y. Yu, "Performance prediction of large-scale parallell system and application using macro-level simulation," in *Proceedings of the 2008 ACM/IEEE Conference on Supercomputing*, ser. SC '08. Piscataway, NJ, USA: IEEE Press, 2008, pp. 20:1–20:9. [Online]. Available: http://dl.acm.org/citation.cfm?id=1413370.1413391
- [10] A. Ray, T. Srikanthan, and W. Jigang, "Practical techniques for performance estimation of processors," in *Fifth International Workshop on System-on-Chip for Real-Time Applications (IWSOC'05)*, July 2005, pp. 308–311.
- [11] A. Ray, W. Jigang, and T. Srikanthan, "Performance estimation: Ipc," in *Young Computer Scientists, 2008. ICYCS 2008. The 9th International Conference for*, Nov 2008, pp. 189–193.
- [12] G. Prinslow, "Overview of performance measurement and analytical modeling techniques for multi-core processors," *UR L: http://www. cs. wustl. edu/˜ jain/cse567-11/ftp/multcore*, 2011.
- [13] A. Kumar and R. Shorey, "Performance analysis and scheduling of stochastic fork-join jobs in a multicomputer system," *IEEE Transactions on Parallel and Distributed Systems*, vol. 4, no. 10, pp. 1147–1164, Oct 1993.
- [14] J. S. Chang and R. S. Chang, "A performance estimation model for highperformance computing on clouds," in *Cloud Computing Technology and Science (CloudCom), 2012 IEEE 4th International Conference on*, Dec 2012, pp. 275–280.
- [15] J. Vetter, S. Lee, D. Li, G. Marin, C. McCurdy, J. Meredith, P. Roth, and K. Spafford, "Quantifying architectural requirements of contemporary extreme-scale scientific applications," in *High Performance Computing Systems. Performance Modeling, Benchmarking and Simulation*, ser. Lecture Notes in Computer Science, S. A. Jarvis, S. A. Wright, and S. D. Hammond, Eds. Springer International Publishing, 2014, pp. 3–24. [Online]. Available: http://dx.doi.org/10.1007/978-3-319-10214-6 1
- [16] A. Bhatele, L. Wesolowski, E. Bohm, E. Solomonik, and L. V. ´ Kale, "Understanding application performance via micro-benchmarks ´ on three large supercomputers: Intrepid, Ranger and Jaguar," *Int. J. High Perform. Comput. Appl.*, vol. 24, no. 4, pp. 411–427, Nov. 2010. [Online]. Available: http://dx.doi.org/10.1177/1094342010370603

TABLE IV PREDICTED PERFORMANCE FOR THE PROCESSOR OF INTEREST

| Application | Measured Time (Haswell) | Predicted Time (Future Xeon) | Projected Improvement (%) |
| --- | --- | --- | --- |
| NAMD | 0.215 | 0.189 | 12.3 |
| GROMACS | 45.4 | 38.9 | 14.2 |
| QE | 303.2 | 249.1 | 17.9 |
| WRF | 84.6 | 54.8 | 35.2 |

- [17] R. Fatoohi, "Performance evaluation of NSF application benchmarks on parallel systems," in *Parallel and Distributed Processing, 2008. IPDPS 2008. IEEE International Symposium on*, April 2008, pp. 1–8.
- [18] A. Tiwari, A. Gamst, M. Laurenzano, M. Schulz, and L. Carrington, "Modeling the impact of reduced memory bandwidth on HPC applications," in *Euro-Par 2014 Parallel Processing*, ser. Lecture Notes in Computer Science, F. Silva, I. Dutra, and V. Santos Costa, Eds. Springer International Publishing, 2014, vol. 8632, pp. 63–74. [Online]. Available: http://dx.doi.org/10.1007/978-3-319-09873-9 6
- [19] D. J. Kerbyson, "A look at application performance sensitivity to the bandwidth and latency of Infiniband networks," in *Proceedings of the 20th International Conference on Parallel and Distributed Processing*, ser. IPDPS'06. Washington, DC, USA: IEEE Computer Society, 2006, pp. 274–274. [Online]. Available: http://dl.acm.org/citation.cfm?id=1898699.1898793
- [20] J. D. McCalpin, "System balance and application balance in cost/performance optimization," May 2007, unpublished presentation http://www.cs.virginia.edu/ mccalpin/SPEC Balance 2007-06-20.pdf.

- [21] J. Michalakes, "Optimizing weather models for Intel Xeon Phi," 2013, intel Theater Presentation SC'13.
- [22] J. D. McCalpin, "STREAM: Sustainable memory bandwidth in high performance computers," University of Virginia, Tech. Rep., 1991-2016, a continually updated technical report http://www.cs.virginia.edu/stream/.
- [23] K. Levenberg, "A method for the solution of certain non-linear problems in least squares," *Quart. J. Appl. Maths.*, vol. II, no. 2, pp. 164–168, 1944.
- [24] "Chameleon home page," https://www.chameleoncloud.org/, accessed: March 2017.
- [25] A. Sodani, R. Gramunt, J. Corbal, H. S. Kim, K. Vinod, S. Chinthamani, S. Hutsell, R. Agarwal, and Y. C. Liu, "Knights Landing: Secondgeneration Intel Xeon Phi product," *IEEE Micro*, vol. 36, no. 2, pp. 34–46, Mar 2016.

