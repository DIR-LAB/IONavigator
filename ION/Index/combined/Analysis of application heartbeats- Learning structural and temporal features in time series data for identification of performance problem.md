# Analysis Of Application Heartbeats: Learning Structural And Temporal Features In Time Series Data For Identification Of Performance Problems

Emma S. Buneci Duke University Department of Computer Science Durham, NC, USA

emma@cs.duke.edu

## Abstract

Grids promote new modes of scientific collaboration and discovery by connecting distributed instruments, data and computing facilities. Because many resources are shared, application performance can vary widely and unexpectedly. We describe a novel performance analysis framework that reasons temporally and qualitatively about performance data from multiple monitoring levels and sources. The framework periodically analyzes application performance states by generating and interpreting signatures containing structural and temporal features from time-series data. Signatures are compared to expected behaviors and in case of mismatches, the framework hints at causes of degraded performance, based on unexpected behavior characteristics previously learned by application exposure to known performance stress factors. Experiments with two scientific applications reveal signatures that have distinct characteristics during well-performing versus poor-performing executions. The ability to automatically and compactly generate signatures capturing fundamental differences between good and poor application performance states is essential to improving the quality of service for Grid applications.

## 1. Introduction

Large-scale scientific applications from domains as diverse as mesoscale meteorology [8], theoretical physics [31] and high energy physics [1], computational biology [32] and astronomy [17, 3] are both data driven and distributed. They require complex and computationally-intensive analysis, multilevel modeling and real-time data analysis and reduction.

To support the scale and inherent distribution of these applications, significant heterogeneous and geographically distributed resources are required to ensure adequate performance. Running these large-scale applications in such environments poses many challenges including addressing resource contentions, software and hardware failures, and ef-
Daniel A. Reed Microsoft Research 1 Microsoft Way Redmond, WA 98052 daniel.reed@microsoft.com ficiently handling data dependencies. All these potential problems can adversely affect the overall application performance.

Previous efforts in performance diagnosis and optimizations include quantitative mechanisms that assess, based on performance metric thresholds, whether an application's performance expectations are being met at a given point [29, 30, 33]. Threshold-based techniques are a form of service level agreements (SLAs) for scientific Grid applications. Such approaches are definitely useful to a user who knows: (1) the key metrics to monitor, and (2) the best value of the threshold that would capture the most important performance problems without triggering too many false alarms.

The major weakness of threshold-based approaches that rely on static, non-adaptive thresholds is the assumption that these meaningful threshold values are known in advance.

This is seldom true in practice. In a complex and dynamic environment such as a Grid, on which different applications with varied characteristics execute, finding meaningful performance metric thresholds may be very difficult. Furthermore, from a usability perspective, threshold-level approaches work well if there are relatively few metrics specified and monitored, and if the impact of these metrics on the application performance, both individually and as a set, is simple and easy to understand and predict.

In this paper, we propose an alternative and novel performance analysis methodology that addresses the disadvantages of static threshold-based approaches by learning differences between characteristics of performance time series data during good and degraded application performance states. Our approach redefines and expands the concept of a SLA in terms of the qualitative notion of performance as perceived by the scientific application user. Instead of depending on a user to specify a set of numerical thresholds within a SLA (i.e., the application's memory utilization should be 1 GB, and the available network bandwidth should be in the range of [100 Mb s 300 Mb s]), our framework relies on the user to express his or her level of satisfaction with various executions of the application by labeling these executions as having a desirable or undesirable performance1.

From such labeled sets of scientific Grid applications executions, we seek to define and extract features of the monitored performance data that correlate with this qualitative notion of performance. Formally, we associate characteristics of low-level performance metrics with higher-level application performance states. For example, consider a case where the user is unsatisfied with the recent executions of his or her application, as the average run times may be twice as long as previous runs. There could be different and multiple causes of degraded application performance such as more competition for network bandwidth, changes of configuration in the computational environment or application source code changes, to name a few of the possibilities. Our framework's goal is twofold: to automatically detect (1) the existence of a possible problem, and (2) the type of problem affecting application performance during executions.

Practical and user-centric qualitative performance analysis approaches are especially important as we continue to develop Grid applications atop high performance computing
(HPC) systems with thousands of processors and complex execution dynamics. We summarize our main contributions below:
1. User-centric definition of a scientific Grid application SLA in terms of a qualitative notion of performance; 2. Novel definition of an application's performance *temporal signature* in terms of structural and temporal features of performance time series data; 3. Characterization of *temporal signatures* associated with both good and degraded application performance states; 4. New visualization techniques for dual-feature, multivariate time series signatures, with practical implications for performance analysis for both application users and system administrators; 5. High-level, qualitative performance problem identification for scientific Grid applications/workflows at both a task level and a global level.

## 2. Performance Analysis Framework

We analyze the structural and temporal characteristics of performance time series data captured during the execution of large-scale Grid applications that can run for many hours or days on many distributed resources. A scientific Grid application is typically composed of various components or tasks that are executed in a certain order as part of a workflow2. Our focus is on the longest-running components within such workflows. The long-running components can be either specific scientific application processing steps or parallel applications, analyzing large amounts of data or performing computationally intensive operations.

We seek to identify *features* in the performance data associated with persistent performance problem-states, and not transient ones, because the costs of triggering any application remediation mechanisms in our context may be too high. We use specific domain knowledge from previous studies of scientific applications [27, 23], and focus on selecting 2Scientific Grid applications are also referred to as scientific workflows.

features of the data encapsulating the knowledge that scientific applications have equivalent classes of behaviors, and that their behaviors as observed by the impact on the computational resources used is described by consistency and regularity of use (e.g., regular and periodic application I/O
of reading and writing data to files).

We take a user-centric approach and define *qualitative performance analysis* as the qualitative performance validation and diagnosis of scientific Grid applications. Qualitative performance validation assesses whether an observed behavior is expected or unexpected as determined by the user.

If the observed behavior deviates from previously observed and common behaviors, a fault-tolerance service such as [15]
triggers some remedial action to maintain application performance within reasonable bounds or to avoid a global application failure. Qualitative performance diagnosis searches the space of unexpected signatures, previously captured and correctly annotated with the known performance problem, for possible causes of unexpected temporal behavior (e.g.,
"low network bandwidth" or "memory leak").

## 2.1 Architecture

Our framework, Teresa3, uses a two-level, bottom-up approach. At the task-level, we analyze the performance of individual application tasks and associate with each a qualitative performance state. At the workflow-level, we derive a global performance state for the entire workflow from each task's performance state. Figure 1 details the architecture. For long-running tasks, Teresa creates, periodically during application execution, performance signatures from time series data. We call these signatures *temporal signatures* because they capture structural features of the data over time.

Temporal signatures are classified based on previously observed signatures. Next, Teresa assesses if observed signatures match expectations. If expectations are not matched, the framework determines what is the most likely cause of the observed behavior and reports the results to a system administrator and to the global application analysis level.

For Grid applications or workflows, Teresa interprets the cumulative qualitative performance states observed in all of a workflow's tasks at a particular time and produces a qualitative assessment of the overall performance.

## 2.2 Task-Level Analysis

For each long-running task in a workflow, buffered real-time monitoring data is periodically (i.e., every 10% of the application's progress toward the final scientific result) analyzed in three steps:
1. Data is transformed into a temporal signature, S,
2. The temporal signature is compared in similarity to known expected temporal signatures, 3. If the temporal signature is dissimilar to expected temporal signatures, it is further compared in similarity to known unexpected/diagnostic temporal signatures.

Teresa's fundamental structure is based on classical supervised learning [10], which requires an offline phase to learn how to distinguish, via temporal signatures, well-performing 3From "temporal reasoning for scientific applications".

![2_image_0.png](2_image_0.png)

executions from poor-performing ones. Expected temporal signatures are generated from application executions during which the application finished successfully and the user was satisfied with the execution time and run time performance of the application. Unexpected temporal signatures can be learned in two modalities: (1) utilize a benchmark such as
[25] to generate known resource contentions, and (2) manually annotate application performance traces where known persistent performance problems were encountered. Using these two approaches, we can build a set database of signatures from known expected and unexpected application performance states. Additionally, each unexpected signature may carry a supplemental label of the possible type and/or source of the performance problem causing the degradation in performance (e.g., Label: [unexpected - *NFS server overload*], or [unexpected - *Memory leak*] ).

## 2.2.1 On-Line Signature Classification: Performance Validation & Diagnosis

Given a new application execution on a set of computing resources, we must determine whether the signatures resulting from the performance data time series are similar to either good states or problematic states. This is a matter of classification; therefore, we apply a simple classification methodology, the nearest neighbor search algorithm [10], and assess which known signature is closest. Various measures of similarity (i.e., Euclidean, city-block, Hamming) can be used on signatures, depending on their definition. As we define our signature S later, we will specify which distance metric is appropriate for our current definition of a signature. If S
is sufficiently similar to members of a class in the expected signature set, then S is considered part of the class. If S is sufficiently similar to members of a class in the unexpected signature set, then the source of the unexpected signature's behavior is deemed similar to the source of the similar signature from the unexpected class.

## 2.3 Workflow-Level Analysis

A large-scale scientific workflow can have hundreds or even thousands of long-running tasks executing concurrently or consecutively on distributed computing resources. To help assess the overall workflow performance, we need mechanisms to (1) validate the performance of the entire workflow and (2) offer probable workflow diagnostics if necessary. At the global application level, we interpret the cumulative qualitative states observed in all of an application's tasks during a time interval. Global performance validation checks the ratio of number of tasks in an undesired performance state, NU , versus the tasks in an expected qualitative state, NE: R
NU NU E
NE NU E 1
. Optimally, one desires NU 0 and NE NU E, such that R 0 when all tasks are in an expected state and R 1 when they are not. The user can specify a threshold for R, TR, that is acceptable to his or her workflow application.

Global performance diagnosis reports, when TR has been surpassed, the type of unexpected behavioral states observed, and the corresponding task and computational resource location where the behavior occurred. A system administrator or application user can utilize this information to learn where the performance problem is across the computational resource space used by the workflow.

## 3. Defining The Application'S Heartbeats: Building Temporal Signatures

Given a set of M uniformly sampled performance time series, Ti, with i 1, *, i,* M, we must find a way to transform performance-relevant information carried in these time series into a compressed signature, S. The signature can be interpreted metaphorically as an application's "heartbeat",
indicative of the health of the application over the span of the execution. Our approach involves extracting a set of features present in each of the Ti time series, which we hypothesize to be useful for differentiating between good and poor application performance states. Examples of features in time series data that could be useful include two categories: (1) statistical features such as mean, variance, or values of various coefficients resulting from transformations of the time series (spectral, auto-correlation, wavelet transformations), and (2) structural features [26], such as a pattern, categorical variance to name some examples.

It should be noticed that, in general, there are two levels of variable selection that must be performed before an actual temporal signature can be generated. At the first level, one must choose the best set of M variables, T1, , TM, which to monitor. At the second level, one must choose a best set of n features f1, , fn which to extract from the M selected variables. In this work, we do not employ automated feature selection as described in [13], but rely on domain knowledge within the context of scientific applications to choose our variables and features. We describe and justify in the next two sections the types of metrics and features we extract.

## 3.1 Variable Selection: Choosing Performance Time Series

The set of performance metrics selected should contain multiple time series metrics because previous research [6] demonstrated that a single metric is insufficient to capture pat-

| Table 1: Set of selected performance time series metrics. Processor Memory Disk Network   |                  |                    |                  |                 |
|-------------------------------------------------------------------------------------------|------------------|--------------------|------------------|-----------------|
| Metric                                                                                    | CPU Utilization  | Memory Utilization | Number of Reads  | Number of Reads |
| Name                                                                                      | Swap Utilization | Number of Writes   | Number of Writes |                 |
| Number of Metrics                                                                         | 1                | 2                  | 2                | 2               |

terns of possible performance violations. Ideally, the metrics should be easily gathered and made available via standard monitoring tools employed at Grid sites. The metrics should be as uncorrelated as possible because the framework employs classification algorithms that produce results sensitive to metric independence. We choose a set of seven quasiindependent metrics, shown in Table 1, which are indicative of the application's use of the four fundamental computing resources within a system: processor, memory, disk and network.

## 3.2 Feature Selection: Choosing Features In Performance Time Series We Focus On Examining Differences In Two Features, F1 And F2, In The Above Set Of Performance Time Series Data:

1. f1: measure of variance in each selected time series, Ti
(e.g., low, moderate, and high variance), and 2. f2: pattern of each time series, Ti (e.g., random, flat, ramp, periodic).

We choose variance within a time series as a feature because it reflects a measure of the spread of the metric values about an expected value. We choose the specified time series patterns for two reasons: (1) they are commonly observed patterns in performance data time series collected during executions of scientific applications, as documented in several studies [27, 23], and (2) within many domains where time series are ubiquitous, these patterns are observed frequently, and are considered primitive patterns [26, 11].

## 3.3 Feature Extraction

Although many empirical time series are non-stationary, we assume that specific intervals or snapshots of the performance data time series we collect meet the weak-stationary condition. Under this assumption, commonly used estimators for sample mean m, and variance s2, and other time series transformations apply [4]. If the time series analyzed will not meet this assumption, the impact on our framework will manifest in a decreased overall classification accuracy for those signatures extracted from nonconforming time series data.

## 3.3.1 Extracting Feature F1, Measure Of Variability

We calculate the sample variance, s2 for each time series collected. Using this metric as the value of our feature would be inappropriate because we want to capture a more relative interpretation of variability which can be compared across computational resources, independent on the scale of the metric. Therefore, we calculate the normalized variance s2n based on knowing the maximum variance ever seen4 for 4Some bookkeeping is required to record the maximum variance seen for each metric across systems.

each metric, s2max. Furthermore, we discretize the normalized variance into three different categorical levels: (1) low,
(2) moderate, and (3) high, corresponding to normalized variance ranges of [0-0.33], [0.34-0.66] and [0.67-1]. We call our measure of variability the *normalized, categorical* variance s2n,c and it will have the categorical values of 1, 2, 3 corresponding to the {low, moderate, high} variability in the data. Therefore, the value of f1 s2n,c, and is extracted for each of the time series of interest, Ti.

## 3.3.2 Extracting Feature F2, Pattern

We want to detect the type of pattern present in the time series because it is an additional indicator of temporal variation in time series. Qualitatively, there is a difference in an application's resource usage patterns between a high transient burst in a relatively uniform metric and a constant, oscillation around a mean. Our pattern identification mech-
IDENTIFY-PATTERN( TIME-SERIES T )
Compute ACF( T ): r(1) ... r(N)
if ( ACF( T ) is defined ) then if ( TEST-RANDOM( T ) is TRUE ) then if ( Variance( T ) is LOW ) then T is FLAT, p=5 else T is RANDOM, p=4 elseif ( TEST-PERIODIC( T ) is TRUE ) then T is PERIODIC, p=3 elseif ( TEST-RAMP( T ) is TRUE ) then T is RAMP, p=2 else Pattern of T is UNKNOWN, p=1 else ( ACF( T ) is undefined )
T is FLAT, p=5 MaxR = max( ACF( T )[2:N] )
MinR = min( ACF( T )[1:N] ) i1 = index( ACF( T ), MinR )
Max2R = max( ACF( T )[i1:N] )
TEST-RANDOM( T )
if r(1,L) <= r(1) <= r(1,U)
return TRUE
TEST-PERIODIC( T )
if MaxR >= r(1,U) AND
MinR <= r(1,L) AND Max2R >= r(1,U)
return TRUE
TEST-RAMP( T )
% min. occurs towards tail of series if index( minR ) >= 70% N
return TRUE
Algorithm 1: Heuristic algorithm for pattern identification for a zero-mean time series, T. anism is based on a combination of a statistical test and heuristics exploiting properties of the auto-correlation function (ACF) for each zero-mean normalized series. Consider a discrete time series T, denoted by z0, , zk, ,zN sampled sequentially at time points τ0, , τk, , τN . The auto-correlation function ACF of T is defined as the set of all auto-correlation coefficients rk at lag k: ACF ( T )
r0, , rk, , rN . Each auto-correlation coefficient rk at lag k can be estimated by computing the auto-covariance coefficient at lags k and zero: rk ck c0 , where ck 1NN k t 1 zt m zt k m , k 0, 1, 2, ,N.

Given a time series T, its ACF transformation will have certain characteristics depending on characteristics of T. For example, if the time series T is random, the auto-correlation coefficients rk beyond lag one (k 1) can statistically be considered zero. The two-tailed test [2] for deciding with 95% confidence that the series is from a random distribution requires a simple comparison that verifies that the value of the first auto-correlation coefficient r1, is between an upper r1,U 1 1.96 N 2 N 1 and lower r1,L 1 1.96 N 2 N 1 confidence band limit. If a series is flat, its auto-correlation function looks flat and its variance is almost zero. If a series is flat with no variance (s2 0), the ACF is undefined. If a pattern is periodic, its auto-correlation function is also periodic. Therefore, values of the auto-correlation coefficients oscillate above and below the confidence band calculated for randomness testing for r1. If the series resembles a ramp (either up or down), then its ACF will monotonically decrease until a minimum value, and then it will increase and damp towards zero, as it approaches the length of the time series, N. This reflects the intuition that values at the beginning of the time series are not correlated with values towards the end of the series.

We show the pseudo-code for the pattern identification algorithm in Algorithm 1; the algorithm produces a pattern identification code, p, with discrete values ranging from one to five, as described in the algorithm. The pattern p will have the categorical values of 1, 2, 3, 4, 5 corresponding to the
{unknown, ramp, periodic, random, flat} patterns present in the data. Therefore, value of f2 p, and is extracted for each of the selected time series of interest, Ti. The accuracy of our proposed pattern detection heuristic algorithm for 10,000 time series of different simulated patterns was found to be 96.1%; due to space limitations, we do not include these results in this work.

## 3.4 Defining A Temporal Signature

We define the temporal signature of a set M of performance time series data as a vector combining two features of interest, f1 and f2 for each of the time series Ti of length N
collected during an application's execution:

$$\begin{array}{r c l}{{{\mathcal{S}}}}&{{=}}&{{[f_{1}(T_{1}),\cdots,f_{1}(T_{M}),f_{2}(T_{1}),\cdots,f_{2}(T_{M})],}}\\ {{{\mathcal{S}}}}&{{=}}&{{[s_{n,c}^{2}(T_{1})\cdots s_{n,c}^{2}(T_{M}),p(T_{1})\cdots p(T_{M})].}}\end{array}$$

Note that in general, different signatures definitions can be explored, but care must be taken in constructing signatures and the corresponding classifier based on these signatures, because the accuracy of the classifier will depend upon the dimensionality of the data (e.g., number of features f in the temporal signature) as well as on the amount of training data points (e.g., number of application experiments which are used for learning a sufficiently accurate knowledge base).

Table 3: Set of system-level performance time series.* indicates we only analyze data for active Ethernet interfaces over which application traffic passes.

i Time Series Metric (Ti) Unit **Abbr.**

1 Available CPU % CPU

2 Memory % Used % MPU 3 Swap % Used % SPU 4 Disk Blocks Read KB/s DBR

5 Disk Blocks Writ. KB/s DBW

6 *Eth 0 or 1 # Pkts. Rcvd. pk/s NR 7 *Eth 0 or 1 # Pkts. Trans. pk/s NT

## 4. Experimental Setting

In this section, we describe the Grid scientific applications, the computing environments and the type of performance time series metrics collected. We summarize our analysis results in Section 5.

## 4.1 Computational Resources And Performance Data Collection

To validate our framework, we conducted experiments using four different system configurations, shown in Table 2, and with two Grid scientific applications, Montage [24] and LEAD [9]. We collected performance time series from available monitoring mechanisms on each system. The time series are a collection of seven performance metrics sampled every second by the sar command, which is part of the sysstat Linux utilities [12]. Metrics names, units, and their abbreviations are identified in Table 3.

## 4.2 Scientific Grid Applications Experiments

Our workload is represented by long-running tasks from two Grid applications, one assembling large-scale sky mosaics, and another performing weather forecasts. Below, we briefly describe these applications.

4.2.1 Montage Workflows: Large-Scale Sky Mosaics Montage [24] is a set of modules that can collectively be used to generate large astronomical image mosaics by composing multiple smaller images. There are five high-level steps to building a mosaic with Montage; they include (1) distributed data query, (2) image re-projection, (3) background modeling, (4) background matching, and (5) image co-addition, resulting in a final large-scale mosaic [24, 16]. Previous experiments with Montage showed that the image re-projection module, mProjExec, dominates execution time
[16]. Therefore, we conduct experiments with this module on two different data sets. One data set, which we label M101, represents 7902 image files from a 15 area of the sky around the spiral galaxy, M101 in the U band obtained from the SDSS data archive. Each file has an approximate size of 5.8 MB, resulting in the total size of the raw data to be approximately 45 GB. The application mProjExec reads all these files and generates re-projections of these images, generating as output a data set of approximately 99 GB. The second data set, which we label M57, represents 7422 image files from a 15 area of the sky around the ring nebula, M57, in the J band obtained from the 2MASS data archive. Due to space considerations, we present only experiments with the M101 data set; all the experiments are listed in Tables

Table 2: Architectural characteristics of computing resource sites.* indicates theoretical network bandwidth

between application data location and compute node location.

Resource Handle slowio lowmem himem **fastcpu**

# Nodes 32 128 128 633 CPU Type Intel Xeon Intel IA64 Intel IA64 Intel IA64

CPU Speed 3.2 GHz 1.3GHz 1.3GHz 1.5GHz

# Processors 2 2 2 2 Memory 6 GB 4 GB 12 GB 4 GB Disk 60 GB 60 GB 60 GB 60 GB Interconnect 1 GigE GigE GigE GigE

Interconnect 2 Infiniband Myrinet Myrinet Myrinet

Network File Sys. NFS PVFS PVFS PVFS Number NFS Servers. 1 54 54 54 *Net. Bandwidth 1 GigE 40 GigE 40 GigE 40 GigE OS Software RedHat SuSE SuSE SuSE OS Version 3.2.3-42 2.4.21-309 2.4.21-309 2.4.21-309

4–7; PPN represents the number of processors per node N on which the application was executed.

Table 4: mProjExec with data-set M101 on fastcpu

Exp. # N:PPN Time(s) Valid? **Expectation**

1336927 64:1 2748 Yes Expected 1336939 64:1 2850 Yes Expected

1337050 64:1 2854 Yes Expected

1337063 64:1 2830 Yes Expected 1337251 32:1 5281 Yes Expected 1337321 32:1 5271 Yes Expected 1337366 32:1 5271 Yes Expected

1337411 32:1 5322 Yes Expected

Table 5: mProjExec with data set M101 on himem.

Exp. # N:PPN Time(s) Valid? **Expectation**

1337732 64:1 3194 Yes Expected 1337764 64:1 3185 Yes Expected

1337812 64:1 3184 Yes Expected

1337845 64:1 3186 Yes Expected 1337573 32:1 6143 Yes Expected

1337603 32:1 6145 Yes Expected

1337652 32:1 6145 Yes Expected 1337696 32:1 6150 Yes Expected

Table 6: mProjExec with data set M101 on lowmem

Exp. # N:PPN Time(s) Valid? **Expectation** 1338089 64:1 3183 Yes Expected

1338104 64:1 3181 Yes Expected

1338112 64:1 3181 Yes Expected

1338145 64:1 3180 Yes Expected

1338205 32:1 6137 Yes Expected 1338452 32:1 6229 Yes Expected

1338563 32:1 6176 Yes Expected

Table 7: mProjExec with data set M101 on slowio.

Exp. # N:PPN Time(s) Valid? **Expectation**

248416 30:1 6332 Yes Unexpected 248418 30:1 5870 Yes Unexpected

248420 30:1 5939 Yes Unexpected

## 4.2.2 Lead Workflows: Real-Time Mesoscale Weather Forecasting

Mesoscale weather –floods, tornadoes, hail, strong wind, lighting and winter storms– causes hundreds of deaths, routinely disrupts transportation and commerce, and results in significant economic losses [28]. Mitigating the impact of such events would imply significantly changing the traditional weather sensing and prediction paradigm, where forecasts are static, linear workflows with no adaptive response to weather. The Linked Environments for Atmospheric Discovery (LEAD) project [9] is currently addressing the fundamental technological challenges of real-time, ondemand, dynamically-adaptive needs of mesoscale weather research. Meteorological data sets and streams generated by radars, satellites, weather balloons and other weather instruments, are transported via shared networks to computing resources for processing. The data types are integrated and transformed such that numerical weather forecast codes can be initiated. Automated data mining algorithms analyzing forecast output can dynamically request new real-time data from instruments when severe weather patterns are detected. The entire or part of the workflow process is repeated following the arrival of new real-time data.

Within such LEAD workflows, the longest-running component is the numerical code, Weather Research and Forecasting (WRF) [22]. Therefore, we conduct experiments with WRF on two different data sets representing weather with different characteristics. One data set, which we label mesoscale, represents a 48-hour forecast during mesoscale weather from 24th October 2001, over a low-resolution of 12 km within the entire continental United States. The input files have an approximate size of 0.34 GB and the output data set is 0.64 GB. The second data set, which we label non-mesoscale, represents a 24 hours forecast during nonmesoscale (i.e., good) weather from November 6th, 2007 over a high-resolution of 4 km in a grid of 1000 km2 within the continental United States. Due to space considerations, we present only experiments with the mesoscale data set; all the experiments are listed in Tables 8–11.

## 5. Results

We generated temporal signatures for all experiments listed for both workflow component applications mProjExec and WRF. In the following sections, we will take a bottom-up ap-

Table 8: WRF2.2 with mesoscale data-set on fastcpu

Exp. # N:PPN Time(s) Valid? **Expectation**

1351014 60:2 1151 Yes Expected 1351287 60:2 1085 Yes Expected

1351292 60:2 1095 Yes Expected

1351297 60:2 1187 Yes Expected

1351634 30:2 1760 Yes Expected

1351643 30:2 1694 Yes Expected 1351702 30:2 1646 Yes Expected

1351752 30:2 1682 Yes Expected

Table 9: WRF2.2 with mesoscale data-set on himem. Exp. # N:PPN Time(s) Valid? **Expectation**

1351487 60:2 1214 Yes Expected

1351581 60:2 1219 Yes Expected

1351625 60:2 1211 Yes Expected 1351628 60:2 1214 Yes Expected

1352492 30:2 1866 Yes Expected

1353639 30:2 1870 Yes Expected

1353659 30:2 1858 Yes Expected

1353833 30:2 1852 Yes Expected

Table 10: WRF2.2 with mesoscale data set on lowmem

Exp. # N:PPN Time(s) Valid? **Expectation** 1351337 60:2 1210 Yes Expected

1351348 60:2 1214 Yes Expected

1351467 60:2 1293 Yes Expected 1351469 60:2 1208 Yes Expected

1351860 30:2 1874 Yes Expected

1351880 30:2 1877 Yes Expected 1351887 30:2 1863 Yes Expected

1351899 30:2 1884 Yes Expected

Table 11: WRF2.0 with mesoscale data set on slowio. Exp. # N:PPN Time(s) Valid? **Expectation**

248477 30:2 4270 Yes Expected

248478 30:2 4223 Yes Expected 248479 30:2 4216 Yes Expected

248480 30:2 4219 Yes Expected

248487 30:2 4213 Yes Expected 143345 30:2 4238 No Unexpected

proach and show: (1) characteristics of individual temporal signatures, (2) characteristics of groups of signatures for one component application and (3) characteristics of signatures across applications and execution platforms. We further describe distinguishing characteristics of good-performing versus degraded performance executions. Finally, we show how one can achieve performance validation and diagnosis via temporal signatures, both at the task and at the workflow level.

## 5.1 Temporal Signatures For Expected Application Executions

Initially, we illustrate the temporal signature for a task within one of the experiments performed. For example, Figure 2 plots the performance time series data collected during the application execution of mProjExec of Experiment 1337251 from Table 4. The temporal signature for the data is a vector of length 14, encoding the normalized, categorical variance and the pattern for each of the seven time series S 1, 1, 1, 1, 1, 1, 2; 3, 1, 5, 5, 3, 3, 3 . Two different visualizations of this signature are shown in Figure 3. The "bars" visualization on the left separates the two features and display the values as bars. The second "color matrix" visualization encodes the five different patterns as five different colors, and it encodes the variance as a bar of 3 different heights within each color box. As various people have different ways to perceive information, it is best to display the same data in forms that appeal to as many uses as possible.

The data and its corresponding signature represent what expected time series look like for this particular task of the selected experiment. Generally, there is low variance on all the metrics, with periodicity detected primarily on the disk and network metrics.

## 5.2 Temporal Signatures For Unexpected Application Executions

Data plotted in Figure 4 represents the execution of Montage on the slowio cluster, where 30 compute nodes attempt to continuously read and write from the network 7902 files totaling a size of 45 GB. This mismatch of running a data intensive application over an low-bandwidth network (i.e.,
there is 1 shared 1 Gb Ethernet link between all the compute nodes and the network file server) has the following effects on the application and environment: (1) the application's run time will be increased because the CPU must wait for the data to arrive from the network (and this behavior is seen in the high variance and periodicity of the CPU
metric), (2) the operating system keeps allocating memory buffers to handle the file IO requests submitted by the application. We believe that this allocation goes unbounded, as one observes the memory utilization on the system to be slowly but consistently increasing until all the memory of the system is fully utilized. While this behavior may be the result of a possible memory leak of the application, we believe that this is not the case, as the swap memory metric remains at zero even after all the memory on the system has been used. Figure 6 shows a comparison of expected and unexpected signatures for Montage. Notice how visually we can quickly note a difference between the expected (a) and unexpected
(b) application executions.

## 5.3 Framework Evaluation

We quantify the accuracy of our classification (i.e., performance validation and diagnosis of our framework) based on temporal signatures by applying cross-validation on the existing data for both the WRF and Montage experiments. We employ K-fold cross-validation, with K 25. The average balanced accuracy (B.A.) rate for WRF for data set mesoscale from Table 11 for 25 validation tests was 0.84, while the average B.A. rate for Montage for data set M101 was 0.79 while for Montage data set M57, the average B.A. rate was 0.81. These results support the hypothesis that given new performance time series data for these two applications, our temporal signature methodology will be able to validate and diagnose, with a reasonable degree of accuracy, the run-time performance of scientific applications.

## 5.3.1 Workflow Level: Performance Validation And Diagnosis Consider A Simple Instantiation Of A Lead Workflow Where 60 Wrf Tasks Run In Parallel On Compute Nodes On The

![7_image_0.png](7_image_0.png)

slowio cluster and 32 WRF tasks execute on the himem cluster. The total number of concurrently monitored tasks is 92.

The user specifies a threshold value of TR 0.1, representing the ratio of unexpected to expected behavioral observations he or she is willing to tolerate. At periodic intervals correlated with application progress, the framework generates temporal signatures across all tasks.

The following two scenarios illustrate global performance validation and diagnosis. During the first analysis interval, all tasks executing on the himem cluster are classified as belonging to an expected behavioral state, while all tasks executing on the slowio cluster also belong to an expected behavioral class previously observed on that particular system.

The threshold value R 0 because there are no unexpected states. Since R Tr, the overall qualitative performance of the workflow is deemed expected.

During the next analysis interval, all the qualitative signatures generated on the slowio cluster reveal a strong similarity with signatures from the unexpected behavioral signatures associated with perturbations due to an overloaded NFS server. The threshold value R 0.48 becomes greater than the user specified value TR 0.1. The framework therefore reports that the overall qualitative performance state of the workflow is undesired with the possible diagnostic being a potential NFS server problem on the slowio cluster.

## 6. Discussion And Future Directions

This approach has the advantage of simplifying for the user the methodology by which to specify in practice an SLA for a scientific workflow application. However, a disadvantage may be the factor of subjectivity's on what constitutes good and poor application performance for a set of scientific users of a given workflow application. Similarly with the work by Cohen [7], we associate low-level performance metrics with high-level application performance states, and learn characteristics of the metrics that correlate with good and degraded performance states in the context of large-scale scientific Grid applications. Our framework generates compact signatures from multiple time series and associates essential features present in data with an application's expected and unexpected performance states. The generated signatures are of constant size for each task analyzed, and this makes our framework scalable to many performance time series metrics across many resources. This characteristic is necessary for any scalable performance analysis technique processing monitored data across HPC systems with thousands of processors. Furthermore, given the complex execution dynamics of Grid applications, a qualitative approach becomes essential to understanding application performance, because it offers an easy way for the application user to grasp what may be wrong with the distributed application and what can be done to fix the underlying problem.

Since it relies on a supervised learning technique, the approach is dependent on acquiring relevant training samples from both performance states; the more representative of the possible sample space, the more accurate and beneficial such a methodology is. The difficulty lies in recording as many signatures as possible associated with unexpected states, since these typically are rare performance instances that are hard to trigger on systems. However, this disadvantage can be overcome with a combination of (1) an autonomous on-line signature learner, that could continuously

![8_image_1.png](8_image_1.png)

![8_image_2.png](8_image_2.png)

![8_image_0.png](8_image_0.png)

expand based on new observations- the learned signatures database, and (2) an active unexpected signature learner, constructed with the help of a synthetic benchmark system perturbation that can be used to alter the performance of the application in a controlled way.

Exploring alternate signature definitions. In our current work, we focused on two examples of features of performance time series data: variance and pattern. Our highlevel approach suggests that a similar approach should work with other features (e.g., within a periodic pattern one may care about the amplitude and frequency of periods). Future experiments will test this hypothesis.

Understanding the signature space across scientific applications. Our experiments with two scientific workflows showed that signatures of different scientific applications are similar. We can only make this claim for the small set of applications and experiments conducted; however, it would be an interesting research direction to explore whether there are classes of scientific applications which will result in similar signatures in both expected and unexpected states for a given set of performance metrics; this would be useful to easily adapting a new scientific workflow to our performance analysis framework.

Extending workflow-level analysis. We have employed a simple approach to interpreting the overall workflow performance state, where each task is given an equal weight of importance to the overall workflow performance quality and

![9_image_1.png](9_image_1.png)

![9_image_0.png](9_image_0.png)

(b) Color Matrix Visualization

![9_image_2.png](9_image_2.png)

Figure 6: Signatures for various application runs for expected and unexpected performance states for application mProjExec. Each row within an application experiment represents the temporal signature of one of the 32 tasks (a) or 30 tasks (b), which are executing on a different computational resource.

every undesired performance state has the same qualitative effect on the overall performance. Our current approach may be inappropriate for certain workflows that either have tasks of significantly greater importance to the user or overall workflow performance, or when certain unexpected states are much more important to detect than others.

## 7. Related Work

Our framework uses concepts and techniques spanning several areas, including time series analysis, pattern recognition, dimensionality reduction and compression, learning algorithms for problem diagnosis, and high-dimensional data visualization. We apply these techniques in the context of performance analysis for scientific Grid applications. Below, we compare and contrast our research to some key works from the above mentioned research areas. Application and System Signatures. Cohen et al. [7]
presents a method for automatically extracting an indexable signature that distills the essential characteristics from a system state. Our work is similar in generating and cataloging compact signatures associated with system state but it differs as temporal signatures are extracted from time series data and our applications of interest are long-running and scientific, which have an effect on the types and amount of variability observed in trace data. Another key similarity is that, similarly to Cohen, we associate low-level system metrics with higher-level application states. Lu and Reed
[20] describe compact application signatures for parallel and distributed scientific codes, an approach that summarizes the time-varying resource needs of applications from historical trace-data. Application signatures are used in combination with performance contracts [35] to validate execution performance. Our work is similar in scope, in trying to obtain compact signatures from historical trace data of applications; however signatures are more intuitive in that they are associated with a user-guided state of performance. Jain [14] describes examples of visual signatures of performance problems, displayed with the help of Kiviat graphs. These simple visual performance signatures represent an early approach of qualitatively describing a good (i.e., graph has star-like appearance) versus a bad (i.e., graph looks more like a polygon than a star) system state. Similarly to the indexable signatures of [7], our temporal signatures are meant to be used for automated detection of expected and unexpected performance states. Furthermore, similarly to Kiviat graphs, our signatures are designed to support a human system administrator in quickly detecting problematic states of performance across a Grid application's execution, improving current system monitoring tools such as Ganglia [21] or MonALISA [18]. Feature Extraction in Time Series. Methodologies and applications for feature selection and extraction in time series abound in many domains. Within the context of very large time series, there are an abundance of techniques that have explored methods for time series clustering and compression based on feature extraction and representation; a notable recent technique is SAX [19]. We believe there are vast amount of opportunities for using techniques developed in the space of time series clustering and compression together with multi-dimensional data visualization designed for user-centric performance analysis approaches.

Performance Analysis for Scientific Workflows. A set of recent works address the issue of performance analysis of scientific workflows, in particular SCALEA-G [34], and the K-WfGrid project [33]. Our approach can use data provided at the workflow level by an integrated Grid performance monitoring tool such as SCALEA-G, and transform it to a compact representation so as to learn essential characteristics of data that correlate well with workflow performance states. Performance monitoring and visualization tools such as those in [5] are very valuable since they enhance the support provided to a scientific user to understand the performance of a workflow. However, they do rely on the user to
"analyze" the data charts, plots and other visual information.

This analysis process may be reasonable for a user with prior experience to performance analysis tools and for inspection of moderate amounts of data and plots. However, when the workflow scales to thousands of nodes, and the amounts of data monitored is very large, even experienced performance analysts will have difficulties understanding the performance of the analyzed workflow. Our approach represents a small-step towards a self-assessing and self-diagnosing performance framework, where we rely a user's notion of a successful and well-performing workflow or activity execution to learn patterns in the performance data associated with these qualitative performance states.

## 8. Conclusions

We described Teresa, a novel performance analysis framework, aimed at validating and diagnosing the performance of large-scale scientific Grid applications. Teresa generates temporal signatures of applications from performance time series data and classifies them based on previously observed signatures. Teresa assesses if observed signatures match user-defined expectations of performance. If expectations are not matched, the framework investigates the causes of altered performance and suggests possible problem explanations to the application user or system administrator. Experiments validating the framework showed that (1)
there exist common temporal signatures characterizing wellperforming executions of scientific codes, and (2) qualitative performance validation and diagnosis is achieved if we can define and build temporal signatures capturing fundamental differences in data from good and degraded performance states.

9. REFERENCES
[1] Worldwide Large Hadron Collider (LHC) Computing Grid Project. http://lcg.web.cern.ch/LCG/.

[2] R. L. Anderson. Distribution of the Serial Correlation Coefficients. *Annals of Mathematical Statistics*,
8(1):1–13, 1941.

[3] B. G. Berriman, E. Deelman, J. C. Good, J. Jacob, D. Katz, C. Kesselman, A. C. Laity, T. Prince, G. Singh, and M.-H. Su. Montage: A Grid Enabled Engine for Delivering Custom Science-Grade Mosaics on Demand. In *Proc. of SPIE: Astronomical* Telescopes and Instrumentation, volume 5487, Glasgow, Scotland, 2004.

[4] G. Box and G. Jenkins. Time Series Analysis:
Forecasting and Control. Holden-Day, 1970.

[5] P. Brunner, H.-L. Truong, and T. Fahringer.

Performance Monitoring and Visualization of Grid Scientific Workflows in Askalon. In *High Performance* Computing and Communications, volume 4208, pages 170–179. Springer Berlin / Heidelberg, 2006.

[6] I. Cohen, M. Goldszmidt, T. Kelly, J. Symons, and J. Chase. Correlating Instrumentation Data to System States: A Building Block for Automated Diagnosis and Control. In *Proceedings of the OSDI*, 2004.

[7] I. Cohen, S. Zhang, M. Goldszmidt, J. Symons, T. Kelly, and A. Fox. Capturing, Indexing, Clustering, and Retrieving System History. In *In Proceedings of* SOSP, Brighton, United Kingdom, 2005.

[8] K. Droegemeier. Linked Environments for Atmospheric Discovery. Technical report, University of Oklahoma, 1st July 2005.

[9] K. Droegemeier, D. Gannon, D. Reed, B. Plale, J. Alameda, T. Blatzer, K. Brewster, R. Clark, B. Domenico, S. Graves, E. Joseph, D. Murray, R. Ramachandran, M. Ramamurthy, L. Ramakrishnan, J. A. Rushing, D. Weber, R. Wilhelmson, A. Wilson, M. Xue, and S. Yalda.

Service-Oriented Environments for Dynamically Interacting with Mesoscale Weather. Computing in Science and Engineering, 7(6):12–29, 2005.

[10] R. O. Duda, P. E. Hart, and D. G. Stork. *Pattern* Classification. John Wiley & Sons, Inc, 2nd edition, 2001.

[11] D. G. Galati and M. A. Simaan. Automatic Decomposition of Time Series into Step, Ramp, and Impulse Primitives. *Pattern Recognition*,
39:2166–2174, 2006.

[12] S. Godard. The Sysstat Utilities.

http://perso.orange.fr/sebastien.godard/.

[13] I. Guyon and A. Elisseeff. An Introduction to Variable and Feature Selection. Journal of Machine Learning Research, 3:1157–1182, 2003.

[14] R. Jain. *The Art of Computer Systems Performance* Analysis. John Wiley and Sons, Inc, 1991.

[15] G. Kandaswamy, A. Mandal, and D. A. Reed. Fault Tolerance and Recovery of Scientific Workflows on Computational Grids. In Workshop on Resiliency in High-Performance Computing in conjunction with CCGrid 08, 2008.

[16] D. S. Katz, G. B. Berriman, E. Deelman, J. Good, C. Kesselman, A. C. Laity, T. A. Prince, G. Singh, and M.-H. Su. A Comparison of Two Methods for Building Astronomical Image Mosaics on a Grid. In 7th Workshop on High Performance Scientific and Engineering Computing (HPSEC-05), 2005.

[17] A. C. Laity, N. Anagnostou, B. G. Berriman, J. C.

Good, J. Jacob, D. Katz, and T. Prince. Montage: An Astronomical Image Mosaic Service for the NVO. In Astronomical Data Analysis Software and Systems XIV, ASP Conference Series, volume XXX, 2005.

[18] I. C. Legrand, H. B. Newman, R. Voicu, C. Cirstoiu, C. Grigoras, M. Toarta, and C. Dobre. Monalisa: An Agent Based, Dynamic Service System to Monitor, Control and Optimize Grid Based Applications, September 2004.

[19] J. Lin, E. Keogh, P. Patel, and S. Lonardi. Finding Motifs in Time Series. In *2nd Workshop on Temporal* Data Mining, Edmonton, Alberta, Canada, 2002.

[20] C.-d. Lu and D. A. Reed. Compact Application Signatures for Parallel and Distributed Scientific Codes. In *Proc. SC '02*, 2002.

[21] M. L. Massie, B. Chun, and D. Culler. The Ganglia Distributed Monitoring System: Design, Implementation, and Experience. *Parallel Computing*,
30(7), 2004.

[22] J. Michalakes, J. Dudhia, D. Gill, T. Henderson, J. Klemp, W. Skamarock, and W. Wang. The Weather Research and Forecast Model: Software Architecture and Performance. http:
//wrf-model.org/wrfadmin/docs/ecmwf_2004.pdf, 2004.

[23] E. L. Miller and R. H. Katz. Input/Output Behavior of Supercomputing Applications. In *Proceedings of the* ACM/IEEE Conference on Supercomputing, pages 567–576, Albuquerque, New Mexico, 1991.

[24] The Montage Project: An Astronomical Image Mosaic Engine. http://montage.ipac.caltech.edu/, 2007.

[25] J. Moore. Gamut: Generic Application EMULaTOR.

http://issg.cs.duke.edu/cod/, 2004.

[26] R. T. Olszewski. *Generalized Feature Extraction for* Structural Pattern Recognition in Time-Series Data. PhD thesis, Carnegie Mellon Univeristy, 2001.

[27] B. K. Pasquale and G. C. Polyzos. A Static Analysis of I/O Characteristics of Scientific Applications in a Production Workload. In *Proc. SC '93*, pages 388–397, Portland, Oregon, United States, 1993.

[28] R. A. Pielke and R. Carbone. Weather Impacts, Forecasts, and Policy. *Bulletin of the American* Meteorological Society, 83:393–403, 2002.

[29] R. Prodan and T. Fahringer. Dynamic Scheduling of Scientific Workflow Applications on the Grid: A Case Study. In *20th Symposium of Applied Computing*,
pages 687–694, Santa Fe, New Mexico, USA, 2005. ACM Press.

[30] D. Reed and C. Mendes. Intelligent Monitoring for Adaptation in Grid Applications. *Proceedings of the* IEEE, 93(2), 2005.

[31] R. Sugar. National Computational Infrastructure for Lattice Gauge Theory.

http://www.scidac.gov/physics/quarks.html.

[32] D. Sulakhe, A. Rodriguez, M. D'Souza, M. Wilde, V. Nefedova, I. Foster, and N. Maltsev. Gnare: An Environment for Grid-Based High-Throughput Genome Analysis. In *CCGrid '05*, Cardiff, UK, 2005.

[33] H.-L. Truong, P. Brunner, T. Fahringer, F. Nerieri, R. Samborski, B. Balis, M. Bubak, and K. Rozkwitalski. K-Wfgrid Distributed Monitoring and Performance Analysis Services for Workflows in the Grid. In e-Science and Grid Computing (e-Science
'06), Amsterdam, The Netherlands, 2006.

[34] H. L. Truong and T. Fahringer. Scalea-G: A Unified Monitoring and Performance Analysis System for the Grid. In Second European AcrossGrids Conference, AxGrids 2004, volume 3165, pages 202–211, Nicosia, Cyprus, 2004. Springer-Verlag.

[35] F. Vraalsen, R. A. Aydt, C. L. Mendes, and D. A.

Reed. Performance Contracts: Predicting and Monitoring Grid Application Behavior. In Proc. 2nd International Workshop on Grid Computing, 2001.