# Using Performance-Power Modeling to Improve Energy Efficiency of HPC Applications

COVER FEATURE COVER FEATURE **ENERGY-EFFICIENT COMPUTING ENERGY-EFFICIENT COMPUTING**

![](_page_0_Picture_1.png)

Energy-efficient scientific applications require insight into how high-performance computing system features impact the applications' power and performance. This insight results from the development of performance and power models. When used with an earthquake simulation and an aerospace application, a proposed modeling framework reduces energy consumption by up to 48.65 and 30.67 percent, respectively.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

High-performance computing (HPC) systems especially petaflops-scale supercomputers currently consume a tremendous amount of power. As of November 2015, the top five supercomputing systems consume an average of 10 megawatts (MW), with an average performance of 17.54 petaflops (www.top500.org/lists/2015/11). Taking into consideration the goal to eventually achieve exascale systems with 20 MW of power, such systems will be greatly constrained by power and energy consumption,

so a unique approach to balancing power and performance is required.

To this end, it is important to understand the relationships among runtime, power consumption, and the unique characteristics of each large-scale scientific application—for instance, looping constructs, data structures, data movement, communication overlapping, synchronization, and so on. Insights about these relationships provide guidance for application optimizations to reduce power and energy. These optimizations

### **SAVING ENERGY INTUITIVELY IMPLIES A REDUCTION IN POWER CONSUMPTION, RUNTIME, OR BOTH.**

might involve application modification, system tuning, or a combination of both.

We propose an energy-saving framework to model application runtime, system power, CPU power, and memory power based on hardware performance counters. We rank and correlate the counters from these models to identify the most important counters for application optimizations and improve the application energy efficiency. We also develop a Web-based what-if prediction system to estimate the outcomes of the possible optimizations theoretically.

#### **CONSERVING POWER AND ENERGY**

There are many application optimization approaches to reducing runtime, such as algorithm optimizations, loopnest optimizations, and compiler optimizations. There are numerous programming models, languages, and runtime systems that, when applied thoughtfully, can also reduce runtimes. Most vendors use power-monitoring techniques at the hardware level to dynamically reduce various resources' power consumption. This can be as simple as spinning down disks and down-clocking idle cores or as complex as implementing asynchronously clocked circuits. Today, nearly all microprocessors contain numerous dynamic resource allocation techniques to conserve power, while still delivering on-demand performance.

In addition, two software-based techniques currently exist for reducing the power consumption of arbitrary workloads. First, dynamic voltage and frequency scaling (DVFS) dynamically adjusts the CPU frequency over a given time window based on both policy and demand. Second, the dynamic concurrency throttling (DCT) technique adapts the level of concurrency at runtime under similar constraints.

Saving energy intuitively implies a reduction in power consumption, runtime, or both. This means that all research in this area can be classified into three categories: reduce time and power, reduce time but allow an increase in power, and reduce power while allowing an increase in time. Energy E is the average power W over time T: E = T × W. To clarify the three categories, we assume that the percentage change of time is a (0 < a < 1), and the percentage change in power consumption is b (0 < b< 1), compared with a baseline from which modifications are made. The following simple mathematical analyses of the three categories will help clarify these concepts.

#### **Reduce time and power**

Assuming that the reduced time is T × (1 – a) and the reduced

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

power consumption is W× (1 – b), we have the reduced energy T × (1 – a) × W × (1 – b) = (1 – a)(1 – b) × T × W *<* T × W. In this case, the energy is saved by 1– (1 – a)(1 – b) = a + b – ab.

Matthew Curtis-Maury and his colleagues achieved a significant reduction in energy (19 percent mean) by implementing simultaneous power savings (6 percent mean) and performance improvements (14 percent mean) using DVFS and DCT.1 Dong Li and his colleagues followed a similar approach, achieving an average energy savings of 4.18 percent with a performance gain of up to 7.2 percent.2 In our previous work, we were able to reduce the runtime by up to 14.15 percent and simultaneously reduce power consumption by up to 12.50 percent using DVFS, DCT, and code modifications.3

#### **Reduce time and increase power**

Assuming that the reduced time is T × (1 – a) and the increased power consumption is W × (1 + b), we have the resulting energy: T × (1 – a) × W × (1 + b) = (1 – a)(1 + b) × T × W. A reduction in energy occurs if (1 – a)(1 + b) × T × W < T × W—in other words, b – a – ab < 0. If b ≤ a, energy saving occurs. This approach is common in methods that reduce runtime via an increase in resource utilization (increase in concurrency).

#### **Reduce power and increase time**

Assuming that the increased time is T × (1 + a) and the reduced power is W × (1 – b), we have the resulting energy: T × (1 + a) × W × (1 – b) = (1 + a)(1 – b) × T × W. A reduction in energy occurs if (1 + a)(1 – b) × T × W < T × W; in other words, a – b – ab < 0. If a ≤ b, energy saving occurs. This approach is common in methods that use DVFS. Most applications spend time waiting on everything besides the CPU, so slowing down the CPU frequency saves more power than it costs in performance. This concept led to the development of new architectures from vendors such as IBM (Blue Gene), SiCortex (MIPS), and Calxeda (ARM).

In this article, we use performance and power modeling to guide energy-efficient application developments using the first two categories (reducing time and power, and reducing time and increasing power) because the Blue Gene/Q system (Argonne National Library's Mira supercomputer) has only one CPU frequency setting (1.6 GHz).

#### **PERFORMANCE AND POWER MODELING**

Accurately measuring or estimating power consumption is essential in this work. Because direct online power measurement at high frequencies is impractical, hardware performance counters are widely used as effective proxies to estimate power consumption. These counters are currently incorporated in most modern architectures. They monitor system components such as processor, memory, network, and I/O by counting specific events such as cache misses, pipeline stalls, floating-point operations, bytes in/ out, bytes read/write, and so on. Statistics for such events can be collected at the hardware level with little or no overhead. This makes performance counters a powerful means to monitor an application, analyze its hardware resource usage, and estimate its runtime and power consumption.

Much of the previous research on power modeling and estimation is based on performance counters.4–6 Researchers used performance counters to monitor multiple system components and then attempted to correlate this data with the power consumed by each system component. They used that correlation to derive a model that could estimate the power consumption for each system component. The accuracy of their results depended on the choice and availability of the performance counters, the benchmarks and applications that were evaluated, and the specific statistical data-fitting methods used. Many of the approaches used a small set of performance counters (often less than 10 counters) for power modeling.

In our previous work,3 we developed four different models for the metrics—runtime, system power, CPU power, and memory power—based on 40 performance counters. We found that the performance counters used for each of the different models were not the same. In studying six scientific applications, we found that a total of 37 different per-

## **PERFORMANCE COUNTERS ARE A POWERFUL MEANS TO MONITOR AN APPLICATION AND ESTIMATE ITS RUNTIME AND POWER CONSUMPTION.**

formance counters were used for the models, and only three or four counters were the same from model to model.

 In our latest study, to develop models for runtime and power consumptions, we collected 40 available performance counters on one system with different system configurations (number of cores and number of nodes) and

application problem sizes. We then used a Spearman correlation and principal component analysis (PCA) to identify the major performance counters (r1,r2 …,rn (n < 40)), which are highly correlated with the metric runtime, system power, CPU power, or memory power. Then we used a nonnegative multivariate regression analysis to generate our four models based on the small set of major counters and CPU frequency (f).

For the model of runtime t, we developed the following equation:

$$t=\beta_{{}_{0}}+\beta_{{}_{1}}\times r_{{}_{1}}+...+\beta_{{}_{n}}\times r_{{}_{n}}+\beta\times\frac{1}{f}\,,\tag{1}$$

where β0 is the intercept, βn is the regression coefficient for the performance counter rn, and β is the coefficient for the CPU frequency f.

Similarly, we modeled CPU power consumption p using the following equation:

$$p=\alpha_{0}+\alpha_{1}\times r_{1}+...+\alpha_{n}\times r_{n}+\alpha\times f^{3}.\tag{2}$$

In this case, α0 is the intercept, αn is the regression coefficient for the performance counter rn, and α is the coefficient for the CPU frequency f. The equations for system power and memory power models are similar to Equation 2.

#### **MODELING AND ENERGY-SAVING FRAMEWORK**

Figure 1 shows a general diagram of our proposed counterbased modeling and energy saving framework. We used

the Multiple Metrics Modeling Infrastructure (MuMMI)7 to collect the performance counters as well as the four metrics we wanted to correlate with and uploaded the data to a MuMMI database. MuMMI provides a Web-based modeling system to automatically generate the runtime and power models based on the counter and metric data from the MuMMI database. All performance counters were normalized against the total number of cycles during execution to create performance event rates for each

counter. Next, we performed a Spearman correlation and PCA to identify the significant counters that correlate with the four metrics. Then, we used a nonnegative multivariate regression analysis to generate each of the four models, based on the reduced set of counters and CPU frequencies using Equations 1 and 2. Our previous work3,7 indicates that

![](_page_2_Picture_20.png)

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

![](_page_3_Figure_0.png)

**FIGURE 1.** Modeling and energy-saving framework. The process collects data for available counters, runtime, system power, CPU power, and memory power; builds performance and power models; predicts performance and power; and provides recommendations for energy savings. HPC: high-performance computing; PAPI: Performace API; PCA: principal component analysis.

the runtime and power models have a prediction error rate of less than 7 percent on average for the six scientific applications used.

Building on the four models for the metrics, we implemented a counterranking method to identify which of the measured counters made a significant contribution. These counters were then used to guide application modifications to achieve a reduction in both runtime and power consumption.

#### **Counter-correlation analysis and ranking**

Once we had the runtime, system power, CPU power, and memory power models, we then identified the most significant performance counters for each.

The ranking algorithm, shown in Figure 2, works as follows. First, we created a counter list consisting of the counters

with the highest coefficient percentage. These counters have the highest ratio of their coefficient to the sum of the all coefficients from the four models in the order of runtime, system power, CPU power, and memory power. Second, in the same order, we eliminated the insignificant counters (those with less than 1 percent) from the counter list. Finally, we analyzed and sorted the correlations among these counters using a pairwise Spearman correlation to identify the counters that most significantly contribute to the models to form the final counter list. We pruned the

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

![](_page_3_Figure_8.png)

**FIGURE 2.** Counter-ranking algorithm. Based on the counters from each model, the most important counters are identified across the four models.

final list so that if a counter with a higher rank was highly correlated with a counter of a lower rank, the counter with the lower rank was eliminated. This resulting list of counters was used to guide application modifications.

#### **Recommendation for energy savings**

As we mentioned earlier, performance counter values are correlated with the application properties that affect performance and power. Many code optimizations solely focus on improving cache reuse to reduce the application runtime

![](_page_4_Figure_1.png)

**FIGURE 3.** A Web-based what-if prediction system. Based on performance and power models, the outcomes for runtime, system power, CPU power, and memory power are predicted theoretically if the number of translation lookaside buffer instruction misses (TLB_IM) is reduced by 20 percent.

because memory access is known to be a bottleneck for most architectures. However, these efforts are often based on performance data from just a few runs with little consideration of data dependency, problem size, and system configuration. Furthermore, these optimizations tend to ignore the power consumption issue.

In our work, the performance and power models are generated from different system configurations and problem sizes, thus providing a broader understanding of the application's usage of the underlying architecture. This in turn results in more knowledge about an application's energy consumption on a given architecture. For instance, if we identify the counters r1 and r2 as the most important—r1 dominates in the runtime model and r2 dominates in the power models—and find them to be uncorrelated, then our application modifications will focus on both counters. In this way, our modifications not only reduce the application runtime but also its power consumption. However, using general-purpose, power-unaware performance tools like gprof, TAU, ScoreP, HPCToolkit, HPM Toolkit, and CrayPat, the impact of the counter r2 might go entirely unnoticed.

Consider the following: assume that ri , rj , and rk are three performance counters that contribute significantly to the runtime model (Equation 1) or power model (Equation 2) for the system, CPU, or memory, and ri is identified as the most significant. ri is correlated to rj with the value of 0.9, and to rk with the value of 0.6. If the value of the counter ri is reduced by 20 percent, then the value of rj is reduced

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

by 18 percent (0.9 × 20 percent), and the value of rk is reduced by 12 percent (0.6 × 20 percent). Under this assumption, we use Equations 1 and 2 to predict the theoretical impact on runtime and power consumption.

Based on runtime and power models and counter correlations, we developed a Web-based what-if prediction system to predict the theoretical outcomes of possible optimizations (see Figure 3). With our system, for instance, given the Parallel Multiblock Lattice Boltzmann (PMLB) application,8 if the number of translation lookaside buffer instruction misses (TLB_IM) is reduced by 20 percent, the correlated counters are reduced based on their correlation values with TLB_IM, and the runtime is

reduced by 4.13 percent. The average node power is almost the same, and CPU and memory power consumption are slightly reduced.

The question then becomes, how can we reduce the value of the counter ri by 20 percent? This requires a thorough understanding of the application characteristics and the portion of the underlying architecture that affects that particular metric. Jan Treibig and his colleagues discussed several typical code performance patterns that are mapped to some hardware metrics and can assist in code optimization.9 It is important to realize that users could easily misinterpret generalized performance counters, like PAPI (Performance API; http://icl.cs.utk.edu/papi) presets, on different architectures. Users must look up the exact definition in the architecture manual and understand how the application characteristics and the underlying architecture units affect the counters.

#### **CASE STUDIES: PERFORMANCE COUNTER-GUIDED ENERGY OPTIMIZATION**

We use two scientific applications—the parallel aerospace application PMLB8 and the parallel earthquake simulation eq3dyna10—to discuss performance counter-guided energy optimization on two power-aware supercomputers: Mira (the Blue Gene/Q system at the Argonne National Laboratory) and SystemG (the x86-64 system at Virginia Tech).

The PMLB application uses the D3Q19 lattice model, corresponding to 19 velocities in 3D—including collision and streaming—and is written in C, MPI, and OpenMP. eq3dyna is a parallel finite-element simulation of dynamic earthquake ruptures along geometrically complex faults and is written in Fortran90, MPI, and OpenMP.

#### **PMLB on SystemG**

Figure 4 shows the performance counter rankings of the four models using 15 different counters for PMLB with a 128 × 128 × 128 problem size on SystemG. We applied the ranking algorithm from Figure 2 to the counters for each of the four models. From the most to least significant, they are TLB_IM, VEC_INS (vector/single-instruction, multiple data [SIMD] instructions), TLB_DM (translation lookaside buffer data misses), and L2_ICM (level 2 instruction cache misses). We used a pairwise Spearman cor-

relation to analyze the correlations between the two highest-ranked counters (TLB_IM and VEC_INS) as follows:

TLB_IM: Contributed in runtime TLB_DM: Corr Value=0.89217296: Contributed in runtime L2_ICM: Corr Value=0.88451013: Contributed in runtime

VEC_INS: Contributed in system, CPU, memory

We found that the TLB_IM counter only contributes in the runtime model and that it is correlated with TLB_DM and L2_ICM. VEC_INS, however, contributes in the system power, CPU power, and memory power models and is not correlated with any other counters. Therefore, we focus our optimization efforts on TLB_IM and VEC_INS on SystemG. Theoretically, using our what-if prediction system, reducing the number of TLB_IM by 20 percent results in a 4.13 percent reduction in runtime; accelerating the VEC_INS by 20 percent leads to a 1.85 percent reduction in node power.

The Linux system on SystemG supports two page sizes: a 4-Kbyte default and 2 Mbytes for huge pages. A single

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

![](_page_5_Figure_8.png)

**FIGURE 4.** Ranking for the original Parallel Multiblock Lattice Boltzmann (PMLB) on SystemG. Fifteen different counters are used for four models. The ranking is based on the coefficient percentage for each counter.

2-Mbyte huge page only requires a single TLB entry, whereas the equivalent amount of memory would need 512 TLB entries using 4-Kbyte pages. As such, enabling such page sizes for an application with a performance that is bound by TLB misses can be a significant benefit. We enabled the 2-Mbyte pages for the application execution using the libhugetlbfs library (https://github.com/libhugetlbfs /libhugetlbfs) to reduce the TLB misses. We also vectorized the code and used the compiler option -ftree-loopdistribution to perform loop distribution, which improves cache performance on big loop bodies and allows further loop optimizations like vectorization to take place.

Figure 5 shows the results of these optimizations. SystemG has eight cores per node. We observed a decrease in application runtime by an average of 11.23 percent (Figure 5a), with an increase in system power by an average of 0.01 percent (Figure 5b). The CPU power increases by an average of 2.13 percent in Figure 5c, and the memory power increases by an average of 0.61 percent in Figure 5d. Overall, this represents an average energy savings of 11.28 percent. Note that the average energy-saving percentage (11.28 percent) is bigger than the runtime improvement percentage (11.23 percent), meaning that reducing the runtime and power saves more energy.

![](_page_6_Figure_1.png)

![](_page_6_Figure_2.png)

![](_page_6_Figure_3.png)

**FIGURE 5.** Runtime and average power comparison. Our optimizations resulted in (a) a decrease in application runtime by an average of 11.23 percent, (b) an increase in system power by an average of 0.01 percent, (c) an increase of CPU power by an average of 2.13 percent, and (d) an increase of memory power by an average of 0.61 percent.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

#### **PMLB on Mira**

For the 10 performance counters used in the four models for PMLB with the 512 × 512 × 512 problem size on Mira, our ranking algorithm results in the following counters, from highest to lowest: HW_INT (number of hardware interrupts), BR_MSP (conditional branch instructions mispredicted), VEC_INS, L1_ICM (level 1 instruction cache misses), FDV_INS (floating-point divide instructions), and BR_NTK (conditional branch instructions not taken).

We used a pairwise Spearman correlation and found that the HW_INT counter only contributes in runtime and does not have any correlated counters; however, BR_MSP is correlated with the L1_ICM, VEC_INS, and BR_NTK counters. VEC_INS is correlated with BR_ MSP, L1_ICM, FDV_INS, and BR_NTK. FDV_INS is one of two main counters in the runtime model, and L1_ICM is the dominant one in the memory model. Based on this information, we focus our optimization efforts on the counters BR_MSP and VEC_INS on Mira. Theoretically, using our what-if prediction system, reducing the number of BR_MSP by 20 percent results in a 2.07 percent reduction in runtime and a 1.44 percent reduction in node power; accelerating the VEC_INS by 20 percent leads to a 1.32 percent reduction in node power and a 4.18 percent reduction in runtime.

To reduce branch mispredictions, we inlined several procedures, unrolled several loops, and eliminated some conditional branches. Mira features a quad floating-point unit (FPU) that can be used to execute four-wide SIMD instructions or two-wide complex SIMD instructions. We utilized the quad FPU to accelerate the vector operations using the compiler option –qarch=qp –qsimd=auto and used up to four OpenMP threads per core for the program executions.

![](_page_7_Figure_0.png)

![](_page_7_Figure_1.png)

The total energy saved by these optimizations was an average of 15.49 percent for the problem size of 512 × 512 × 512 (Figure 6), where 2,048 × 64 stands for 2,048 nodes (1 message-passing interface [MPI] process per node) with 64 OpenMP threads per node (4 threads per core; 16 cores per node). The average percentage of energy savings (15.49 percent) is bigger than the percent improvement in runtime (14.85 percent). For the 128 × 128 × 128 problem size, the average total energy saved is 26.64 percent. Overall, the average total energy saved is 18.28 percent over the two problem sizes (128 × 128 × 128 and 512 × 512 × 512) on up to 32,768 cores on Mira.

#### **eq3dyna on SystemG**

For the 14 performance counters used in the four models for eq3dyan with the problem size of 200m (element resolution), the ranking algorithm results in the following counters, from highest to lowest: L1_ICM, L2_ICA (level 2 instruction cache accesses), L2_DCW (level 2 data cache writes), L2_TCW (level 2 total cache writes), and TLB_DM. We found that the counter L1_ICM is a common counter for the four models and is a dominant factor (more than 93 percent) in three power models. However, L2_ICA only contributes in the runtime model. They are highly correlated because level 1 instruction cache misses cause the increase of level 2 instruction cache accesses. The other counters L2_DCW, L2_TCW, and TLB_DM are minor. Based on this information, we focus our optimization efforts on L1_ICM.

We looked at the source code to determine which section of the code contributed significantly to the runtime. We found that two major functions qdct3 and hrglss are the area of focus and also found a pattern that many blocks were originally expanding 8 × 3 to 24 × 3 sparse blocks, so we rewrote this part of the code so that it no longer expands to improve cache locality performance. As a result, more data was able to fit in the L1 cache to reduce cache misses. To further reduce the L1 instruction cache misses, we added the compiler option -fprefetch-loop-arrays to prefetch caches and memory to improve the performance of loops that access large arrays. The total energy saved by these optimizations was an average of 30.67 percent for eq3dyna with the problem size of 200m on up to 256 cores.

#### **eq3dyna on Mira**

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

We applied the ranking algorithm to eight performance counters used in the four models for eq3dyna with the

![](_page_8_Figure_1.png)

**FIGURE 7.** Node energy comparison for eq3dyna. With the increase of cores to 4,096, the energy-saving percentage for the optimized one is an average of 61.73 percent, and the optimized one has good scalability.

problem size of 100m on Mira and found that VEC_INS is a common dominant factor in runtime, system power, and CPU power models. BR_MSP had the second-highest rank and is a dominant factor in the memory power model. Based on this information, we focus our optimization effort on VEC_INS and BR_MSP.

We utilized the Blue Gene/Q's quad FPU to accelerate the vector operations using the compiler option –qarch=qp –qsimd=auto and used up to four OpenMP threads per core for the program executions. We fused several loops, unrolled several loops, and eliminated some conditional branches to reduce the BR_MSP. We also removed two MPI process synchronizations to improve the overlapping of computation and communication.

The optimized application was run with the problem size of 100m on up to 4,096 cores. The total energy saved by these optimizations was an average of 61.73 percent (see Figure 7). For the problem size of 200m, the total energy saved by these optimizations was an average of 20.61 percent. Overall, the average total energy saved was 48.65 percent over the problem sizes of 100m and 200m on up to 4,096 cores.

Note that, based on our experiments, setting the environment variable OMP_DYNAMIC=true to apply DCT to the optimized application executions did not improve performance or energy because of the overhead caused by enabling dynamic adjustment of the number of threads. This indicates that our framework saves energy while utilizing all cores.

We believe our framework can be applied to large-scale scientific applications executed on other architectures including hardware like GPGPUs and manycore accelerators like Intel's Xeon Phi. Power and performance models of these applications on one architecture can also be used to predict the power consumption and performance on large-scale systems with similar architectures. Our methodology represents a generalizable approach to comprehensive optimization, focused on the most efficient use of available resources and balancing runtime with

power consumption. We hope our method can help application and system developers create the next generation of energy-efficient applications and supercomputers.

#### **ACKNOWLEDGMENTS**

This work was supported by National Science Foundation under grants CCF-1619236, CNS-0911023, and DMS-1317131. We thank B. Duan from Texas A&M University for providing the earthquake simulations with different problem sizes, K. Cameron of Virginia Tech for the use of PowerPack and SystemG, the Argonne Leadership Computing Facility for the use of BlueGene/Q Mira under DOE INCITE project PEACES, and the reviewers for their valuable comments.

#### **REFERENCES**

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

- 1. M. Curtis-Maury et al., "Prediction Models for Multidimensional Power-Performance Optimization on Many Cores," *Proc. 17th Int'l Conf. Parallel Architectures and Compilation Techniques* (PACT 08), 2008, pp. 250–259.
- 2. D. Li et al., "Hybrid MPI/OpenMP Power-Aware Computing," *Proc. IEEE Int'l Symp. Parallel and Distributed Processing* (IPDPS 10), 2010; doi:10.1109/IPDPS.2010.5470463.
- 3. C. Lively et al., "E-AMOM: An Energy-Aware Modeling and Optimization Methodology for Scientific Applications on Multicore Systems," *Computer Science—Research and Development*, vol. 29, no. 3, 2014, pp. 197–210.

- 4. G. Contreras and M. Martonosi, "Power Prediction for Intel XScale Processors Using Performance Monitoring Unit Events," *Proc. Int'l Symp. Low Power Electronics and Design* (ISLPED 05), 2005, pp. 221–226.
- 5. K. Singh, M. Bhadhauria, and S.A. McKee, "Real Time Power Estimation and Thread Scheduling via Performance Counters," *ACM SIGARCH Computer Architecture News*, vol. 37, no. 2, 2009, pp. 46–55.
- 6. K. Sugavanam et al., "Design for Low Power and Power Management in IBM Blue Gene/Q," *IBM J. Research and Development*, vol. 57, nos. 1–2, 2013; doi:10.1147/JRD.2012.2227034.
- 7. X. Wu et al., "MuMMI: Multiple Metrics Modeling Infrastructure," *Tools for High Performance Computing 2013*, A. Knüpfer et al., eds., Springer, 2014, pp. 53–65.
- 8. X. Wu et al., "Performance Analysis, Modeling and Prediction of a Parallel Multiblock Lattice Boltzmann Application Using Prophesy System," *Proc. IEEE Int'l Conf. Cluster Computing* (CLUSTR 06), 2006; doi:10.1109/CLUSTR.2006.311876.
- 9. J. Treibig, G. Hager, and G. Wellein, "Performance Patterns and Hardware Metrics on Modern Multicore Processors: Best Practices for Performance Engineering," *Euro-Par 2012: Parallel Processing Workshops*, LNCS 7640, I. Caragiannis et al., eds., Springer, 2013, pp. 451–460.
- 10. X. Wu, B. Duan, and V. Taylor, "Parallel Simulations of Dynamic Earthquake Rupture Along Geometrically Complex Faults on CMP Systems," *J. Algorithm and Computational Technology*, vol. 5, no. 2, 2011; http:// faculty.cs.tamu.edu/wuxf/papers/jact2010.pdf.

# **ABOUT THE AUTHORS**

**XINGFU WU** is a TEES Research Associate Professor in the Department of Computer Science and Engineering at Texas A&M University. His research interests include performance evaluation and modeling, power modeling, parallel and cloud computing, and energy-efficient computing. Wu received a PhD in computer science from Beijing University of Aeronautics and Astronautics. He is the author of *Performance Evaluation, Prediction and Visualization of Parallel Systems* (Kluwer Academic Publishers, 1999). Wu is a Senior Member of ACM and a member of the IEEE Computer Society. Contact him at wuxf@tamu.edu.

**VALERIE TAYLOR** is a senior associate dean of Dwight Look College of Engineering, regents professor, and the holder of the Royce E. Wisenbaker Professorship at Texas A&M University. Her research interests include high-performance computing, performance evaluation and modeling, power modeling, and energy-efficient computing. Taylor received a PhD in electrical engineering and computer science from the University of California, Berkeley. She is an IEEE Fellow and a member of ACM. Contact her at vtaylor@tamu.edu.

**JEANINE COOK** is a principal member of the technical staff in the Scalable Architectures Group at Sandia National Laboratories and an affiliate faculty member at New Mexico State University, where she directs the research of several PhD students. Her research interests include processing-in-memory architectures, next-generation memory technologies and subsystems, performance analysis tools for exascale systems, and performance modeling and simulation. Cook received a PhD in computer science from New Mexico State University. She received the Presidential Early Career Award in Science and Engineering for her work in performance modeling. Contact her at jeacook@sandia.gov.

**PHILIP J. MUCCI** is the president and cofounder of Minimal Metrics, LLC as well as a research consultant for the Innovative Computing Laboratory at the University of Tennessee. His research interests include high-performance computing, performance optimization, and performance analysis tools. Mucci received an MS in computer science from the University of Tennessee. Contact him at phil@minimalmetrics.com.

Selected CS articles and columns are also available for free at **http://ComputingNow.computer.org.**

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:15:23 UTC from IEEE Xplore. Restrictions apply.

