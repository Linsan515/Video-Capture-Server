## Check List


### Inspection checks

#### Data Faults
(1)是否所有variables在使用之前，都被初始化過了？

(2) 所有的常數constants有被命名嗎？

(3)有任何的機率發生 buffer overflow嗎？

#### Control faults
(4)每一個loop的確定會結束嗎？


#### Input/out faults
(5)所有input variables 都被使用了嗎？

(6)非預期的input variables 會導致 corruption嗎？

(7)所有的output變數都有被assign value後，才output出來嗎？

### Interface faults
(8)假如components access 分享memory，那這些components 有分享相同的 **model** of the shared memory structure

### Storage managements
(9)假使存取空間不在被使用，那這些空間會被動態調整嗎？

(10)假使動態記憶體被使用，存取空間會有動態調整嗎？



