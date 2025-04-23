# Application Parallel Test with Parameter of High Performance Computer

Zhenyu Liu Shanghai Key Laboratory of Computer Software Evaluating and Testing Shanghai, China Email: lzy@ssc.stn.sh.cn

Lizhi Cai Shanghai Key Laboratory of Computer Software Evaluating and Testing Shanghai, China Email: clz@ssc.stn.sh.cn

Yun Hu Shanghai Key Laboratory of Computer Software Evaluating and Testing Shanghai, China Email: huy@ssc.stn.sh.cn

*Abstract***— This paper studies the test and evaluation methods for parallel application in high-performance computers. The parallel performance of specific application could be attributed to its multiple application parameters. The basic test methods are proposed for application evaluation. The test results are analyzed to achieve application performance further. Finally, performance results are analyzed through parameter evaluation in parallel application performance testing.** 

## *Keywords- Performance Test; High Performace Computer, Test Evaluation*

## I. INTRODUCTION

High performance computer (HPC) is known as supercomputers, which composed by a number of computing units. The High performance computer has characterizes of high computing speed, storage capacity, high reliability of computer systems. The high-performance computer systems are used for high-performance computing to solve some complex problems that ordinary computers cannot solve, such as Meteorology Region, Energy Region, and Medicine Region and so on. Some other fields are also need high-performance computing that different types of computing needs, including computer-intensive, communication-intensive, and store intensive.

Computer architecture consists of symmetric multiprocessor (SMP), distributed shared memory (DSP), and massive parallel processing (MPP), the cluster computer system (Cluster). Any processor of the SMP architecture computer can directly access memory address, therefore the performance of access latency, bandwidth, access probability are equivalent. Distributed shared memory (also known as the CC-NUMA, Cache Directory of non-uniform memory access) architecture computer is limited physical memory modules for each processor, but the logical users are shared total memory. The delay and bandwidth in memory access is inconsistent differences in 3-10 times between local and remote. Each node of the cluster computer system is a complete computer, the various nodes interconnected by high-performance networks, network interfaces and I/O bus is loosely coupled connections, each node has a complete operating system.

The general purpose of high-performance computer test mainly covers the performance trend analysis, performance bottleneck analysis.

Based on test results, performance trend is analyzed the potential performance according to the different configuration and its test result. Standard test programs should be provided to the specification of a control test conditions and procedures, including the test platform environment, the input data, output results and performance indicators. The practical effect is studies on different machine configurations, the resulting performance with the CPU, memory, network, operating system and other factors on system performance variation.

Performance bottlenecks analysis is an important issue for high-performance computers. The performance evaluation is aims to make better use of high-performance computer. The high performance computers play the advantages of carry out variety of testing. The requirement for high-performance evaluation will be concluded in the following situations:

- Computer selection. There are very differences for various fields of application for same highperformance computers. The high-performance computers must pass the specific performance test for the field of application features. For example, the specification states that the field of meteorology program design and the overall requirements of the HPC benchmark, test items and test methods, test results, both qualitative and quantitative assessment methods. Technically, the test results to determine the technical parameters of the tender will be suitable for the introduction of the test specification applications of meteorological characteristics in the field of high performance computers in the field of meteorology, the size of the machine will be able suitable system with the least effort and economy.
- Check failure: high performance computer should use a large amount of computing time during the calculation according to the complexity of the program architecture. The calculation is finished and the result is obtained. However, performance-related failures are generally not shown. There will be a variety of unexpected failure under high load conditions. To

![](_page_0_Picture_17.png)

reproduce these failures and scenario must be executed by means of performance tests. For example, some research found that the cluster network communication performance LU mode Myrinet2000 than the normal Fast Ethernet worse [1]. Some research focus on another point of view of the parallel program performance optimization environment caused by a different cluster network (cLAN).

- System development: in the process of development of high-performance systems, due to the complexity of its structure, you must verify that each system meets the original design requirements. High-performance computer evaluation is a key factor in the computer system development. Previous research stage in the system, the system development phase, the system acceptance and qualitative phase have different study methods and means
The main structure of this paper is as follows: the second part of existing research is given. Section 3 introduces the test method for application parallel test. The next part gives a detailed experiment and its result analysis. Finally, there are conclusions and future works.

# II. RELATED WORKS

Measuring computer work load and speed indicators two most important indicators of the IPS [2] and FLOPS is [3]. IPS (Instructions per Second) is a method of calculating the transactions execution speed of the computer central processing unit. FLOPS (Floating-point the Operations per Second) is the number of floating point operations per second executed. IPS and FLOPS are not fully characterizing the system performance. IPS is different in the field of transaction processing according to different instruction sets, the instruction function and complexity vary widely.

The efficiency test programs of the data transmission have the LLCBench evaluation package and MPBench SKaMPI [4][5]. The LLCBench test developed by the University of Tennessee, package composed by three sub-programs such as MPBench, CacheBench, BLASBench.

NAS Parallel Benchmark(NPB) is developed by NASA Ames Research Center. NPB is a parallel computer performance evaluation benchmark in a field of scientific computing, which contains eight different benchmarks are from the calculation of fluid dynamics CFD (Computational Fluid Dynamics) software, each benchmark test simulates different behavior in parallel applications [6].

For testing these two important indicators of a large number of benchmarks, the study consists of the floating point performance Linpack evaluation, multi-CPU efficiency evaluation, the MPI data transfer performance evaluation, cache performance evaluation, Linear Algebra Subprograms performance evaluation [7]. Too much researcher is emphasis deficiencies about processor floating-point computing performance [8]. In [9], a new evaluation standard HPCC (HPC Challenge Benchmark) is developed, HPCC attempt to more fully reflect the parallel high-performance for Linpack performance in computer systems. HPCC standard consists of 28 evaluation criteria in seven categories, including Linpack, covering computing performance, memory access performance, the interconnection network performance [10].

HPC is the HPL program in the field of high performance computing, the most widely used benchmark. It uses pivoting Gaussian elimination method and purpose of test program is measuring the time required for solving dense linear equations.

The SimpleScalar simulator is open software that source code is open architecture simulator [11]. As for data locality analysis of the program, you can modify the SimpleScalar simulator to output the the memory access sequence and Cache failure information into file, to achieve a partial analysis for the program [12]. It is recommended that the application designer with the memory angle tuning and evaluation tester study the effect of performance tuning on the basis of performance test results [13].

The available peak performance of the computer measured is very different in practical application. There are many reasons, such as architecture, applications and programming model. Two methods are used to find the difference between the peak performance and performance in practical application.

- User requirement analysis. Different applications of high-performance computer's CPU or network requirements are varied, such as the defense field applications require a higher response time calculations. The majority of applications in the field of weather forecasting are communication-intensive process. Many applications in bioinformatics require the computing power of the processor. Different areas of application system design to get the core algorithm is also different, which result in the corresponding procedures are also differences. For example, the development of nuclear weapons needs nuclear weapons simulation parallel program, such as SAGE, Sweep3D.
- Memory access characteristics. The analysis of application memory access characteristics is an important approach to improve the performance of parallel programs. Computer, including three different speed cache memory, external memory storage structure. Due to the difference between processor speed and memory speed, CPU memory read data is simultaneously written to cache then the CPU direct access to the cache. Storage performance depends on the level of cache hit rate, that is to say CPU is likely to get reliable data from the cache at any one time. The higher the hit rate, the higher possibility to read data from memory. If the cache do not hit, causing slowdowns. Cache hit rate of any connection with the practical application of memory access model is closely related. According to memory access locality principle, cache hit rate will be higher if access data localized. If read data from memory as far as possible continuous storage, cache hit rate will be higher. The CPU execute the next command is generally in the closed address of the current command which avoid the large-scale far jump. The characteristics of memory access in program are described by data locality,

including the time locality and spatial locality. Time locality is possibility of accessed data repeatedly of the program on the same memory address frequently. Spatial locality is possibility of accessed data which data is used around physical memory space, that is, the sequential read in program physical memory address unit. The program's data locality is characterized by its inherent characteristics, and the system architecture has nothing to do, In fact, the cache of computer system in application program memory access are designed by time locality and spatial locality.

Fixed problem speedup refers to the user to use a larger machine to solve the same problem, it can use the Law Amdahl (Amdahl 's) [13]:

$$\delta_{\rm pa}=\frac{W_{\rm a}+W_{\rm p}}{W_{\rm a}+\frac{W_{\rm p}}{n}}\tag{1}$$

Ws is the serial component of the scale of the problem (that part of the problem cannot be parallelized), Wp is parallel component, n represents the number of processors. If consider

 make serial execution part of the proportion in the entire process.

$$\alpha={\frac{W_{s}}{W_{s}+W_{p}}}\qquad\qquad(2)$$

$$S_{p a}={\frac{\mathrm{n}}{1+(\mathrm{n}-1)a}}\qquad\qquad(3)$$

As can be seen from the formula (3), when the ratio of

serial execution is very small, constant load can be assigned to more processors on speedup obtained close to the n. The

increases , the decreases speedup. (N-1) >> 1, the speedup of parallel systems can achieve the maximum cannot increase the number of nodes to improve system performance.

# III. EVALAUTION AND TESTING

The performance should be evaluated by lots of test execution and numerous analyses for the specific application program.

#### A. *Performance evaluation*

Firstly, consider the high-performance computer systems related to multiple CPUs number or computer nodes. The peak floating-point performance can be achieved by maximum times of floating-point per second in theory. The performance is mainly depends on the CPU frequency and the number of CPU. Here, the speedup and efficiency is given for the parallel system in specific application program.

$$\mathrm{S_{p}=T_{1}\,/\,T_{p}}\tag{4}$$

Ep = Sp / P 

Sp is the speedup, T1 is a single processor execution time and Tp is P-processor parallel system execution time.

Ep is efficiency of parallel system. P is processor number involved in the execution. If Sp = P, the speedup is called linear speedup.

The different between theoretical peak performance and practical measured performance of application for parallel computer are obvious, mainly due to different architecture, different applications and related the programming model. These factors for a particular area in parallel computer systems are based on the common benchmark on the application of performance evaluation in order to accurately determine the performance of the parallel computer system.

## B. *Parameter adjustment*

The parameter evaluation strategy is the key elements for studying the parameter. The difference of test result is important factor to make the decision from many different parameters and various testing environment.

Optimize test is the analyzed program which optimization options for each test are given a number of parameters that allows you to modify. The parallel test is running the optimized code in order to analysis performance trend. In each test iteration, modify the parameter of program must comply with the relevant restrictions, such as reduce the computational accuracy must be verified without modify the input data. Test results must contain the specific hardware and test environments, such as compilers, libraries and so on.

Here, we should consider the test result influence with different parameter. Such for HPCC benchmark, the possible parameter is NB, N, P, Q and operation system and memory size. Therefore, any single-parameter will make the unique testing result own to the parameter adjustment.

TABLE I. TEST RESULT RECORD SHEET

| No | NP | Parameter | Result |
| --- | --- | --- | --- |
| 1 | 16 | OS… |  |
| 2 | 32 |  |  |
| 3 | 48 |  |  |
| 4 | 64 |  |  |

The test strategy in the testing process, the first small-scale training of parametric test matrix, and then proceed to largescale testing phase[13]:

(1) Fixed non-critical parameters (keeping the parameters default), to test and adjust the main parameters, so that the machine measured the peak maximum, and parameters are given the largest measured peak parameter values, and enter the next step parameter adjustment.

(2) Make the key parameters fixed, adjust the non-critical parameters individually, and executed test and measured the system maximum peak performance.

## C. *Testing process*

The basic process consists of four steps: test preparation, environment configuration, test execution and evaluation analysis. The detailed test processes are as follows:

- Test Preparation: analysis of the tested software, combined with the results of analysis of the requirements of the test specifications, configure the machine for the required environment, test design test methods, plans and develop test cases.
- Environment configuration: the environment of the test cases required to prepare the test environment and configuration, to confirm whether the test environment conform to the requirements; install the necessary software and run the package, software compiles and runs normally;
- Test execution: the test environment is satisfied with the test requirements and the requirements of the project parameters in accordance with the test item configuration, then recompile the program if necessary. During testing, data recorded is necessary to get the CPU and memory real-time. When the test is finished, test results are recorded and the test environment is resumed to initial state. Each test case for specific data and parameter should be tested three times at least.
- Evaluation and analysis: analysis impact and trend of different parameters on performance based on test results.

## IV. EXPERIMENTS

According to evaluation and test research of studies, this session is mainly to analyze the influence factors that affect the parallel performance based on numerous experiments. The practical example is n-body problem.

The n-body problem is one of the basic problems of celestial mechanics and general mechanics, as well as the expansion of space in the simulated universe cosmology, astrophysics is now widely used in scientific computing software. These problem are aims to identify multiple objects in known initial position, speed and quality in the case of classical mechanics the follow-up exercise, it can be applied to macroscopic objects can also be applied to micro molecules, atoms. The parameters impact performance of N-body includes: number of processes, TimeLimitCPU, BufferSize and so on.

The Gadget, version 2.0.3 is computing software package used to compute the individual celestial system. Firstly, the environment is prepared to testing. And then parallel performance is tested in the size of the different processes, which named NP. After that, the relevant parameters in the testing process have been adjusted to obtain the total time of the relevant indexes. The total number of steps, calculation of the average time, and calculate the corresponding speedup and parallel efficiency is analyzed based on testing results.

In the experiments, we adopt the two typical data size as the testing data set. The initial data file in Gadget consists of Gadget source code file and Gadget compiler parameter file. The first phase of a smaller data set is complete the test in system environment for different core number in processor, such as 1, 2, 4 and 8. Furthermore, we consider the test results in first phase of the program and data set size. We continue to 16, 32, 48 and 64 core number tests in some supercomputer.

## A. *Small size*

The first phase of testing using the Gadget benchmark in a single processor (one core and four cores), using a variety of different combinations of parameters, repeated test procedures, as far as possible to get more test data from different latitudes the performance impact of parameter changes are summarized, and floating-point computational efficiency of parallel programs, speedup and concurrent efficiency were calculated. Test data using the program default data file, its data size is 276,498. All tests were carried out in the stand-alone multicore environment.

According to the computer CPU and its nuclear number of simulated single-process and multi-process, NP values, respectively 1,2,4,8. The compile parameters and system parameters are set by default.

TABLE II. RESULTS OF SMALL SIZE

| NP | 1 | 2 | 4 | 8 |
| --- | --- | --- | --- | --- |
| Time | 4.0298 | 2.3429 | 1.4241 | 0.8672 |
| Sp | 1 | 1.7200 | 2.8297 | 4.6471 |
| Ep | 1 | 0.8600 | 0.7074 | 0.5809 |

![](_page_3_Figure_14.png)

The figure 1 gives the test result on the default parameter setting based on the Table 2.

Then the different parameters are analyzed. Gadget of the relevant parameters in the testing process has been adjusted, to obtain the total time based on the total number of steps calculation of the average time, and calculate the corresponding speedup and parallel efficiency. These parameters consist of PMGRID, bufferSize for impact of parallel performance during n-body calculation.

# 1) *PMGRID*

PMGRID is behalf of the size of the discrete grid. The Gadget program at compile time, you can adjust parameter setting. The PMGRID option in the makefile is determined whether to use the PM method. If the value of PMGRID is not set, the program calculation did not use the PM method, and then CPU_PM is 0 through the calculation. The default PMGRID value is 128 in the makefile. The results of the PMGRID parameter set to 64,128,192,256 are given:

| TABLE III. |  | PMGRID PARAMETER IN SMALL SIZE |  |  |
| --- | --- | --- | --- | --- |
| PMGRID | NP=4 |  | NP=8 |  |
| CPU |  | CPU | CPU | CPU |
| (Total) |  | (PM) | (Total) | (PM) |
| / | 1.8868 | 0 | 1.1385 | 0 |
| 64 | 1.3229 | 0.0436 | 0.7949 | 0.0255 |
| 128 | 1.2109 | 0.2512 | 0.7495 | 0.1645 |
| 192 | 1.7469 | 0.8979 | 1.1254 | 0.6003 |
| 256 | 2.7023 | 1.91 | 1.7506 | 1.2629 |

256 2.7023 1.91 1.7506 1.2629

![](_page_4_Figure_2.png)

Figure 2. CPU(Total) Varation in different NP and PMGRID

![](_page_4_Figure_4.png)

Figure 3. CPU(PM) Varation in different NP and PMGRID

With increasing PMGRID parameters, the computing time spent on the CPU_PM a corresponding increase. If not set PMGRID parameters, CPU_PM time; as PMGRID the value gradually increased from 64 to 256, CPU_PM time increased from 0 to 1.91 when the NP is 4 and from 0 to 1.26 when NP is 8.

CPU_Total unit (CPU calculating time) with the PMGRID never set gradually increased to 256, the CPU_Total value gradually decreased to a minimum when PMGRID is 128, and then gradually rise. The makefile in PMGRID parameter default value is 128, indicating that the default parameters for the best stand-alone test scenarios.

Theoretically PM algorithm is superior to the BH algorithm. With increasing discrete grid, the PM algorithm advantage will be weakened. In view of CPU_Total unit (CPU calculating time), when compiled parameter PMGRID set the appropriate value, the CPU total calculating time to reach the minimum. The Figure 2 and Figure 3, we can see the CPU_PM results,

PMGRID not set in the BH algorithm in gadgets program, the higher the CPU calculating time; compiled parameter PMGRID set 128, the CPU calculating time to a minimum, and as PMGRID further increase the total CPU calculating time of more than the total CPU run-time using a single BH algorithm.

# 2) *BufferSize*

Buffersize parameter defines cache size (Mb) in the different types using multi-purpose mechanisms in parallel communication. Gadget recommends BufferSize can be between 0-100. The different BufferSize value used to observe the performance impact.

|
|  |

| BufferSize(M) | 5 | 10 | 30 | 50 | 100 | 200 |
| --- | --- | --- | --- | --- | --- | --- |
| CPU_Total | 0.747 | 0.752 | 0.749 | 0.746 | 0.751 | 0.749 |
| CPU_Domain*10 | 0.468 | 0.467 | 0.467 | 0.468 | 0.469 | 0.47 |
| CPU_Predict*100 | 0.888 | 0.886 | 0.877 | 0.874 | 0.89 | 0.896 |
| CPU_TreeWalk | 0.303 | 0.303 | 0.303 | 0.303 | 0.305 | 0.303 |
| CPU_TreeCons*10 | 0.269 | 0.269 | 0.27 | 0.269 | 0.27 | 0.27 |
| CPU_CommSum*100 | 0.607 | 0.607 | 0.602 | 0.604 | 0.606 | 0.608 |
| CPU_PM | 0.162 | 0.167 | 0.165 | 0.161 | 0.163 | 0.163 |

![](_page_4_Figure_14.png)

Figure 4. Varation in different Buffersize

Be seen from Figure 4, as the BufferSize value changes, the total CPU calculating time did not lead to great changes, and other classified calculation time showed no significant changes, did not have a big impact on performance. It can be considered that small cache space will not impact on program running.

# B. *Middle size*

The second phase of testing large-scale multicore environment, using different data size and the combination of the parameters, run the Gadget program, access to test data and analyzes. Test data using a pre-customized data file, its data size is 16,777,216.

The test environment is Cube Supercomputer which provided by Shanghai Supercomputer Center computing environment. The Cube Supercomputer is Linux-cluster system platform which using the SuSE Linux Enterprise Server 10 (x86_64) operating system and infiniband computing network. The n-body software consist of the main Gadget, mvapich 1.0, Fortran compiler pgi, ftww, blas, job management system lsf.

Here, we analysis performance impact with parameter variation on the n-body program calculation. The parameter are processor scale, TimeLimitCPU, and BufferSize.

# 1) *Processores*

The different number processes are carried out to analyze the performance as well as the time factors in the different processes during the test. According to the computer CPU and its simulation process, NP values, respectively 64,128,192,256, which unit is increased by 64 nuclears. The compile parameters, system parameters are the default settings.

TABLE V. RESULTS OF MIDDLE SIZE

| NP | 64 | 128 | 192 | 256 |
| --- | --- | --- | --- | --- |
| Time /10 | 3.9367 | 2.2628 | 1.8332 | 1.7261 |
| Sp | 1 | 1.74 | 2.147 | 2.281 |
| Ep | 1 | 0.86 | 0.7157 | 0.5703 |

![](_page_5_Figure_6.png)

Figure 5. Time, Sp and Ep in Middle Size

Be seen from Figure 5, with increasing number of processes required for single-step time is gradually reduced while the parallel efficiency decreased.

# 2) *TimeLimitCPU*

The parameter TimeLimitCPU defines the upper threshold of calculate time during program execution in Gadget. When TimeLimitCPU set to a smaller value indicates program will stop calculate when calculate time reach the TimeLimitCPU, and the calculation maybe not finished indeed.

|
|  |

| TimeLimitCPU | 10000 | 36000 |
| --- | --- | --- |
| Step | 328 | 766 |
| CPU_Total/10 | 2.6069 | 3.9367 |
| CPU_Domain | 2.4098 | 2.911 |
| CPU_Predict | 0.231 | 0.2674 |
| CPU_TreeWalk/10 | 1.0069 | 1.1111 |
| CPU_TreeCons | 0.5895 | 0.7252 |
| CPU_CommSum | 0.382 | 0.5165 |
| CPU_PM | 1.4296 | 1.9851 |

When TimeLimitCPU is set 10000 and 36000, it is found that the program running will lead to the different number of steps. From the table 6, the step is different in different TimeLimitCPU value when NP value is same, that is 64. When TimeLimitCPU is 10000, the step number is 328, when TimeLimitCPU 36000, the program is running to step number is 766. The different step number indicated that step number increased with growth of the calculating time. With the TimeLimitCPU value increased, the calculating time of program is also increased and lead to the more step number in single test. Figure 6 compares the time and number of steps of performance for two TimeLimitCPU values, 10000 and 36000.

![](_page_5_Figure_14.png)

Figure 6. TimeLimitCPU in Middle Size

#### 3) *Buffersize*

Buffersize parameter defines the different types of code using a multi-purpose communication in parallel mechanisms of cache size. The unit of Buffersize is Mb. Gadget program recommends BufferSize parameter can be between 0-100. During the test, it used to observe the performance in different BufferSize value under NP is 128.

|
|  |

| BufferSize(M) | 10 | 30 | 50 | 70 | 90 |
| --- | --- | --- | --- | --- | --- |
| CPU_Total/25 | 0.767 | 0.592 | 0.536 | 0.542 | 0.55 |
| CPU_Domain/10 | 0.221 | 0.231 | 0.234 | 0.219 | 0.219 |
| CPU_Predict | 0.12 | 0.115 | 0.119 | 0.117 | 0.118 |
| CPU_TreeWalk/10 | 0.512 | 0.512 | 0.512 | 0.512 | 0.512 |
| CPU_TreeCons | 0.323 | 0.328 | 0.326 | 0.32 | 0.322 |
| CPU_CommSum | 0.288 | 0.281 | 0.317 | 0.304 | 0.303 |
| CPU_PM | 0.934 | 0.909 | 0.938 | 0.916 | 0.918 |

![](_page_6_Figure_0.png)

Figure 7. Varation in different Buffersize

The BufferSize parameter, the CPU calculation time gradually decreased and stabilized, while the other detailed CPU calculation time was no significant change seen from Figure 7, does not have a significant impact on performance.

The BufferSize and NP parameter focused on CPU_Total parameters for statistical analysis, data tables are as follows in Table 8 and Figure 8 presents the trend with the BufferSize parameter.

| TABLE VIII. |  |  | CPU_TOTAL WITH DIFFERENT BUFFERSIZE AND NP |  |  |
| --- | --- | --- | --- | --- | --- |
| BufferSize(M) | 10 | 30 | 50 | 70 | 90 |
| NP=64 | 31.4674 | 23.8463 | 20.9572 | 20.3 | 20.1581 |
| NP=128 | 19.1518 | 14.6671 | 13.316 | 13.4563 | 13.806 |
| NP=160 | 17.1281 | 13.3077 | 12.6807 | 12.9102 | 12.8095 |
| NP=192 | 15.8707 | 12.8004 | 11.9926 | 13.9888 | 12.1845 |
| NP=224 | 15.1422 | 12.6211 | 12.4546 | 12.3809 | 12.7814 |

![](_page_6_Figure_5.png)

Figure 8. Varation in different Buffersize

## V. CONCLUSIONS & FUTURE WORKS

This paper studied performance test and get the numerous results. The evaluation of different parameters can produce different performance results. The paper summarizes performance results and analyzes performance trend under these various factors and parameters.

Based on the analysis of performance trends and combination of all individual performance influence factors, these testing results provide the method to looking for possible performance bottlenecks and finding system optimization direction through design of high performance computers.

A well designed application and test method could reflect the actual application benchmarks. But for different application, there are various features and test results. For optimizing the performance of existing applications, performance testing also provided ability to improve the application performance by means of adjusts parameter. In the future, we will research into the relation relation between the high performance system and application features should be studies further.

# ACKNOWLEDGMENT

The work is supported by National 863 High-Tech Project under Grant No. 2009AA012201 and Shanghai STCSM Program under Grant No. 08DZ501600.

# REFERENCES

- [1] Tang Y, Sun JC, Zhang YQ, Zhang LB. New consideration on the evaluation model of cluster area network. Journal of Software, 2005,16(6):pp. 1131í1139
- [2] http://zh.wikipedia.org/wiki/MIPS
- [3] http://zh.wikipedia.org/wiki/FLOPS
- [4] LLCBENCH, http://icl.cs.utk.edu/projects/llcbench/
- [5] SKaMPI㧘http://liinwww.ira.uka.de/~skampi/doc.html
- [6] NAS parallel benchmark suite. http://www.nas.nasa.gov/ Software/NPB
- [7] Dongarra JJ, Luszczek P, Petitet A. The LINPACK benchmark: Past, present, and future. Concurrency and Computation: Practice and Experience, 2003,15:SS. 1-18.
- [8] JJ Dongarra, Performance of various computers using standard linear equations software, ACM SIGARCH Computer Architecture News, vol. 20 no. 3 pp. 22–44
- [9] Luszczek P, Dongarra J, Koester D, Rabenseifner R, Lucas B, Kepner J, McCalpin J, Bailey D, Takahashi D. Introduction to the HPC challenge benchmark suite. 2005.
- [10] Liu CY, Wang DS. AHPCC: A high performance computer system evaluation model based on HPCC and analytic hierarchy process. Journal of Software, 2007,18(4):pp. 1039г1046
- [11] G M Amdahl. Validity of Single-Processor Approach to Achieving Large-scale computing Capability. Proc AFIPS Conf, Reston VA, 1967: pp. 483-485
- [12] HPC challenge benchmarkhttp://icl.cs.utk.edu/hpcc
- [13] The SimpleScalar Architectural Research Tool Set, http://pages.cs.wisc.edu/ ~mscalar/simplescalar.html

