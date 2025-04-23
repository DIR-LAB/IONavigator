# **FO-EB-T Package Solution for High Performance Computing**

Po Yuan (James) Su*, David Ho, Jacy Pu, Yu Po Wang

Siliconware Precision Industries Co. Ltd. (SPIL)

No. 123, Sec 3, Chung Shan Rd., Tantzu, Taichung, Taiwan * E-mail: Jamessu@spil.com.tw; Tel: 886-4-25341525 ext. 5075

*Abstract*- It is the famously said by Armstrong in 1969 "That's one small step for a man, one giant leap for mankind." [2]. Neil Alden Armstrong and Buzz Aldrin were landing on the Moon and it is the first time people to land on the Moon [1]. Today, NASA have Artmis program to return astronauts to the lunar surface and going forward to the Moon to stay[3]. This program has supercomputer with high performance computing support to make sure every step will be the best one choice!

Now, High performance computing (HPC) has played the most important role because it can do the caculation quickly and precisely that needs billions or trillions of transistors to support the result comes out. The HPC makes the lager chip size and packaging size design, and it causes lower yield with very experience cost from the 7nm to 3nm wafer node. The strong request for verious chips and devices drive all in one package solution comes out and heterogeneous integration with High Bandwidth Memory (HBM) is the best solution to meet high performance computing application standards. The split die is also the best way to increase wafer good yield rate for cost efficiency and FO-EB-T would be best one choice for this selection.

 The FO-EB-T means the Bridge Die not only has TSV (Through Silicon Via), but also has embedded in fan out package which to do the localized interconnection for High Bandwidth Memory (HBM) with SoC (System on Chip) and this brand new package is for the better electrical performance communications purpose. Comparing with FO-EB package, the FO-EB-T package not only has more flexible layout design advantage, but also still good warpage same as FO-EB package. Besides, the power delivering improve 50% than FO-EB without TSV package. In this paper, we would discuss a FO-EB-TSV packaging design, evaluation and measurement for the electrical performance and warpage mismatch. The paper would demostrate the advantage for this advanced FO-EB-TSV package.

Key words: *High Performance Computing (HPC), High Bandwidth Memory (HBM), Fan-out Embedded Bridge*  *Through Silicon Via (FO-EB-TSV), SoC (System on Chip), Through Silicon Via (TSV)*

## I. **INTRODUCTION**

Fan Out Packages not only have diversify applications but also the most popular packages from small form factor to larger form factor such as the mobile phone and HPC. The FO-EB-TSV one solution has very good performance with efficiency for high density I/O and high speed integration package. By using chiplets with fine-trace TSV ICD technologies achieves package high performance requirement. By using the FO-EB-TSV that we can get higher performance processors for HPC application. Refer to Figure 1 FO-EB-TSV for HPC Product Structure

![](_page_0_Figure_13.png)

Figure 1. FO-EB-T for HPC Product Structure

Today, the internet video streaming service is popular, YouTube, Netflix, Disney Plus, and …etc. All of them will need the HPC for the better experience and Heterogeneous Integration technologies can take this responsibility. Based on the hardware design, chiplets integrated not only can enhance the processor performance, but also the most efficiency for this [4]. That is the package one solution that FO-EB-TSV package not only can provide the lower Coefficient of Thermal Expansion (CTE) mismatch than 2.5D package but also enhance the electrical performance than FO-EB package. Refer to Table 1. Advanced Package Structure Comparison.

| Item |  | 2.5D | FO-EB | FO-EB-T |
| --- | --- | --- | --- | --- |
| Schematic |  |  |  |  |
| Structure | Interconnection | Si Interposer | Si Inter Connect Die + Organic RDL | Si Inter Connect TSV Die + Organic RDL |
| Warpage |  | ★ | ★★★ | ★★★ |
| Performance | Chip Module Stress | ★★ | ★★★ | ★★★ |
| Electric |  | ★★ | *** | ★★★ |
| Ranking |  | ★ | ★★ | ★★★ |

Table 1. Advanced Package Structure Comparison

### II. **PACKAGE ELECTRICAL PERFORMANCE VERFITY**

The HPC request higher bandwidth to increase high performance computing with transmission, it means the high bandwidth memory can achieve this kind of hyper and high speed transmission. The electrical performance comparison table shows FO-EB-TSV and FO-EB Packages. According to the Ohm's law R= V/I, the larger resistance will causes the more power lose. The power of direct current resistance (DCR) simulation shows FO-EB is 38 ohms and FO-EB-TSV is 17 ohms from micro bump to C4 bump distance and it improves 55% power (DCR) which is FO-EB-TSV can provide the better electrical performance than FO-EB. For the Power DCR, we are looking for the less power of DCR and FO-EB-TSV has short distance than FO-EB from C4 bump to micro bump which means the smaller DCR will have better electrical performance. Refer to the Table 2. and Figure 2. PKG Electric Performance for HBM Demand.

![](_page_1_Figure_5.png)

Table 2. PKG Electric Performance for HBM Demand

![](_page_1_Figure_7.png)

Figure 2. PKG Electric Performance for HBM Demand

In terms of prevent the AC noise, the signal protection and stable the voltage is the must request for the package design. By using the IPD capacitor can reduce AC noise, and we put the 3 IPDs to improve the AC noise which is put more IPDs to the different locations. There are 3 locations 1, 2 and 3, and set No IPD as baseline. The first one IPD be mounted on the substrate and the AC noise Diagrams shows improve 15% which is better than without IPD. The second one is to add one more IPD in location 2 will better than only one IPD mount on substrate, and the AC noise shows improve 35% than without IPD. The third one is change the location 2 IPD to location 3, and the result shows it can be improved the 45% of AC noise which is the best than others, and we can see this location is the most close the logic dies [5] [6]. See the Table 3. IPD Demand for Package Electrical Performance.

![](_page_2_Figure_0.png)

Table 3. IPD Demand for Package Electrical Performance

### **III. MODULE STRESS SIMULATION**

For the advanced integration package, the CTE mismatch is the key for this kind of advanced package, and the Stress comparison for 2.5D, FO-EB-T and FO-EB. The different structure interconnection shows the different stress and the FO-EB-TSV with FO-EB shows the better stress simulation than 2.5D package. Refer to the Table 4. Stress Simulation.

| Item | 2.5D | FO-EB | FO-EB-T |
| --- | --- | --- | --- |
| Schematic |  |  |  |
| Structure | Si Interposer | Si Inter Connect Die + | Si Inter Connect TSV Die + |
| Interconnection |  | Organic RDL | Organic RDL |
| Die Corner Module Stress | 1.6X | 1X | 1X |
| RDL Bending | No RDL | 1X | 1X |

Table 4. Stress Simulation

There is the key comparison item for the FO-EB-TSV, 2.5D and FO-EB packages, and it is the die corner stress. We can see every point to represent one package of module size, and we have FO-EB-TSV, 2.5D and FO-EB packages to present 3 colors. The 2.5D package to present blue color, FO-EB-TSV package to present pink color and FO-EB package to present green color. The FO-EB-TSV use the TSV Die to do the heterogeneous integration and the stress shows 1X. The 2.5 package has one big chip module connection for heterogeneous integration, and the stress shows 1.6X which is bigger than FO-EB-TSV stress. The FO-EB also use the die bridge for heterogeneous integration and the stress shows 1X. Based on the stress simulation comparison that the FO-EB-TSV and FO-EBtrends show the same stress and 2.5D package has poor stress simulation. See the Figure 3. Stress Simulation.

![](_page_2_Figure_7.png)

Figure 3. Stress Simulation

Another one item is do the Bending for RDL Stress, and there are FO-EB-TSV and FO-EB to do, and result shows 1X for both of them.

There are 2.5D and FO-EB-T package warpage moiré simulation and refer to the Table 5. 2.5D versus FO-EB-T Packages Warpage Moiré

![](_page_2_Figure_11.png)

Table 5. 2.5D versus FO-EB-T Packages Warpage Moiré

### IV. **WARPAGE MEASURMENT**

 We do the same package size of package warpage moiré for 2.5D with FO-EB-T package. The 2.5D package present the color orange, and FO-EB-TSV package present the color blue for warpage moiré, and the temperature has been setup from 25℃ room temperature to 260℃ high temperature, and we can see the FO-EB-TSV has better contribution with package warpage moiré than 2.5D package at 260℃. See the Figure 4. Packages Warpage for FO-EB-T and 2.5D.

![](_page_3_Figure_0.png)

Figure 4. Packages Warpage for FO-EB-T and 2.5D

Comparing with 2.5D structures, the FO-EB-T has smaller size of TSV die than 2.5D TSI, and FO-EB-T has ratio 1X at 260℃, 2.5D has worse warpage ratio 1.6X at 260℃. The warpage moiré shows FO-EB-T can contribute the better warpage than 2.5D. It was the major benifites to use the 2.5D silicon interposer, but design layout arrangement was constrained with product design. It is the good choice to use FO-EB-TSV for the package design.

### V. **TEST VEHICLE DESCRIPTION**

The test vehicles (TV) design with advanced FO-EB-T technology to see the warpage and reliability data for the FO-EB-T TV demonstration.

In terms of to make sure the package can pass the packaging warpage moiré with various environment. There is a TV demonstration for the FO-EB-TSV package with warpage moiré measurement, reliability and verification confirmation.

### VI. **RELIABILITY TEST PLAN**

The reliability test plan is MSL4, TCJ 3000 Cycles, u-HAST 264 Hours and HTSL1000 Hours [7]. The plan also put the SAT inspection and O/S test. See the Figure 5. Reliability and Test Verification.

![](_page_3_Figure_8.png)

Figure 5. Reliability and Test Verification

There are the warpage Shadow Moiré measurement shows in Figure 6. FO-EB-TSV Warpage Moiré, and it has been setup the JEDEC standard criteria, and this package warpage moiré pass the criteria with customer requirements from 25℃ room temperature to 260℃ high temperature. So the FO-EB-TSV package pass package warpage and customer requirements.

![](_page_3_Figure_12.png)

Figure 6. FO-EB-TSV Warpage Moiré

## **VII. RESULTS**

First, The reliability test items total put 92 samples for T0, and also do the MSL4. The second one is the O/S and F/T for the result verification. Each of u-HAST and HTSL to separate 23 samples to do the O/S and F/T to confirm with good quality. In term of to make sure no delamination and any crack with the FO-EB-T structure, use the SAT to confirm with TCJ, u-HAST and HTSL. All of the reliability test data read point confirmed by O/S, F/T and SAT for the well quality result and passed. See in Table 6. Reliability and Test Verification Result.

| No. | Reliability Test Items | Read Point | Sample Size | SAT & O/S Result |
| --- | --- | --- | --- | --- |
| 1 | Time Zero | TO | 0/92 pcs | All Pass |
| 2 | MSL4 | Pre-cond. | 0/92 pcs | All Pass |
|  | (30 ℃, 60% RH, 96hrs) |  |  |  |
| 3 | TCT (J) | 625, 2000,3000 Cycles | 0/23 pcs | All Pass |
|  | (0 ~ 100 °C) |  |  |  |
| 4 | u-HAST (B) | 132. 264 | 0/23 pcs | All Pass |
|  | (110 °C,85%RH, 17.7 Psia) | Hours |  |  |
| 5 | HTSL (B) | 500. 1000 Hours | 0/23 pcs | All Pass |
|  | (150 ℃, Need Pre-cond.) |  |  |  |

Table 6. Reliability and Test Verification Result

FO-EB-TSV structure had demonstrated the structure cross-section with HBM and SoC dies on the TSV die and FO-EB-T will be the best candidate solution for high performance computing application. Refer to FO-EB-TSV Structure Crosssection in Table 7.

![](_page_4_Figure_0.png)

Table 7. FO-EB-TSV Structure Cross-section

The image shows overall FO-EB-TSV package structure and the SoC, HBM and TSV Dies have been molded. The number 1 photo shows no any crack or damage issue, and the SoC and HBM show good interface. The number 2 photo shows the good joint structure for Cu Stud, RDL, u-Pad and u-Bump, and there is no any non-wetting or delamniation happen. The number 3 photo shows the TSV Die with interface, and the result shows well joints with adhesion. The number 4 shows C4 bump well joint, and the number 5 shows UF filled without delamniation or peeling. The structure crosssection image result shows in Table7. FO-EB-TSV Crosssection.

### **VIII. CONCLUSION**

The FO-EB TSV package had demonstrated with package structure warpage moiré, reliability test and feasibility data, and all of them show the FO-EB-TSV has pass with good result than 2.5D package. The FO-EB-TSV not only has better electrical package design with HBM than FO-EB, but also good package moiré warpage than 2.5D package. The comparison and reliability test result can talk why FO-EB-T Package is the best representative for current high speed with high performance

devices application. We had demonstrated the test vehical (TV)

for FO-EB-T package and provide the result for reliability test and cross-section. All of the reliability test item and result shows the FO-EB-T Package pass all of them and well done the larger package level of reliability test conditions.

### **ACKNOWLEDGMENT**

All of authors would thanks R&D members of technology development team with Quality reliability team for their support on FO-EB-TSV package setup with material, tooling preparation and warpage measurement.

## **REFERENCES**

- [1] Refer English Wikipedia .Org, the free encyclopedia
- [2] Refer Entrepreneur.com

- [3] Refer Certrofisio.com.br
- [4] JEDEC Solid State Technology Association. JESD22-A104C: Temperature Cycling; 2005.
- [5] C. C. Lee et al., "An Overview of the Development of a GPU with Integrated HBM on Silicon Interposer", *2016 IEEE 66th Electronic Components and Technology Conference (ECTC)*, pp. 1439-1444, 2016
- [6] S. Y. Hou et al., "Wafer-Level Integration of an Advanced Logic-Memory System Through the Second-Generation CoWoS Technology", *IEEE Transactions on Electron Devices*, vol. 64, no. 10, pp. 4071-4077, Oct. 2017
- [7] JEDEC Solid State Technology Association, JESD22-B112A: Temperature Cycling Package Warpage Measurement of Surface-Mount Integrated Circuits at Elevated Temperature; 2009.

