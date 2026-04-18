# 术语表 (Glossary)

> `concept_tag` ↔ 中文关键词 ↔ 术语定义 三者的权威映射源。
> **1:1:1 原则**：每个 `concept_tag` 唯一对应一个中文关键词与一条术语定义，严格对齐。
> 设计依据：`docs/plans/2026-04-18-thinking-module-and-concept-graph-design.md` §四、§附录 B。

---

## 列定义

| 列 | 含义 | 格式示例 |
|---|------|---------|
| **concept_tag** | 机器可读 slug；lesson 元信息 / `learner_model.concept_mastery` / prereq-map 均以它为键 | `stm32-eeprom-page-wrap` |
| **中文关键词** | 学习者可见的自然语言短词；思考模块中以反引号包裹使用 | `卷绕机制` |
| **英文** | 英文标准名或学科通用英文表达 | `page wrap` |
| **定义** | 一句话术语解释（避免长段落，详细讲解放 lesson 正文） | `EEPROM 超出页大小时数据覆盖页首` |
| **首次出现** | 主题名 · Lesson 编号；跨主题重复以最早一次为准 | `STM32 · Lesson 3` |

> `concept_tag` 命名格式为 `{topic}-{concept-name}`，全小写、连字符分隔；规范见 `.claude/skills/learning-engine/SKILL.md §4.1 第 6 步`。
> 历史遗留条目若暂无 `concept_tag`，允许填 `—`（与 §九 Q7 决策一致：不强制回填旧 session）。

---

## 数学 (Mathematics)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| — | 函数 | Function | 描述输入与输出之间的对应关系 | 一元函数微分学 |
| — | 导数 | Derivative | 描述函数在某点的瞬时变化率 | 一元函数微分学 |

---

## 心理学 (Psychology)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|

---

## 哲学 (Philosophy)

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|

---

## 计算机科学 / 嵌入式 (Computer Science / Embedded)

### I2C 协议（来自 STM32 通信总线专题 · Lesson 02.0）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| i2c-bus-basics | I2C 总线 | I2C (Inter-Integrated Circuit) | Philips 开发的两线制串行总线，多主多从、引脚少、可扩展 | STM32 · Lesson 02.0 |
| i2c-sda-scl | SDA / SCL | SDA / SCL | I2C 的双向数据线 / 主机产生的时钟线 | STM32 · Lesson 02.0 |
| i2c-open-drain-pullup | 开漏+上拉 | open-drain + pull-up | 设备只能下拉/悬空 + 外部上拉电阻；实现线与逻辑，防电气冲突 | STM32 · Lesson 02.0 |
| i2c-master-slave | 主从架构 | master/slave | 任一时刻一个主机控制 SCL，从机响应地址匹配的请求 | STM32 · Lesson 02.0 |
| i2c-7bit-address | 7 位地址 | 7-bit address | I2C 标准设备地址宽度；左移 1 位后拼 R/W 组成 8 位地址字节 | STM32 · Lesson 02.0 |
| i2c-rw-bit | R/W 读写位 | R/W bit | I2C 地址字节的最低位；0 = 写、1 = 读 | STM32 · Lesson 02.0 |
| i2c-start-stop-signal | 起始/停止信号 | Start / Stop condition | SCL 高期间 SDA 跳变（起始=高→低、停止=低→高）；数据流中不可能出现 | STM32 · Lesson 02.0 |
| i2c-ack-nack | ACK / NACK | ACK / NACK | 第 9 时钟接收端控制 SDA；低 = ACK（继续传）、高 = NACK（结束传） | STM32 · Lesson 02.0 |
| i2c-data-validity | 数据有效性 | data validity | SCL 高期间 SDA 必须稳定；SCL 低时允许切换 | STM32 · Lesson 02.0 |
| i2c-transfer-modes | 三种传输模式 | transfer modes | 标准 100 kbit/s、快速 400 kbit/s、高速 3.4 Mbit/s | STM32 · Lesson 02.0 |
| i2c-compound-rw | 复合读写 | combined format (repeated start) | `S` + `Sr` 两次起始信号——先写寄存器地址（设指针）、`Sr` 不释放总线直接读/写内容；`Sr` 保证事务原子性 | STM32 · Lesson 02.0 |
| i2c-repeated-start | 复始信号 `Sr` | Repeated Start (Sr) | 与 START 电气时序相同的第二次起始信号，但**不释放总线**；是复合读写原子性的物理基础（NXP UM10204 规范） | STM32 · Lesson 02.0 |

### I2C HAL 抽象 & 外设实战（来自 STM32 通信总线专题 · Lesson 02.1）

| concept_tag | 中文关键词 | 英文 | 定义 | 首次出现 |
|-------------|-----------|------|------|---------|
| i2c-hal-api-abstraction | HAL I2C 抽象 | HAL I2C Abstraction | STM32 HAL 层对 I2C 外设的统一封装；`MX_I2C1_Init` + `hi2c1` + `HAL_I2C_*` API | STM32 · Lesson 02.1 |
| hal-i2c-handle | HAL I2C 句柄 | HAL I2C Handle | `I2C_HandleTypeDef hi2c1`，所有 HAL I2C API 的第 1 个参数；封装硬件寄存器 + DMA + 错误码 | STM32 · Lesson 02.1 |
| hal-i2c-mem-write-read | `HAL_I2C_Mem_Write/Read` | HAL I2C Memory Read/Write | 带寄存器地址的读写 API；`Mem_Read` 内置复合读写（`S` + `Sr`），对应 02.0 §3.8 | STM32 · Lesson 02.1 |
| hal-i2c-master-transmit-receive | `HAL_I2C_Master_Transmit/Receive` | HAL I2C Master Transmit/Receive | 纯字节流读写 API，无寄存器地址概念；适合 OLED 刷屏、AHT20 命令等 | STM32 · Lesson 02.1 |
| i2c-7bit-vs-8bit-address-in-hal | HAL 的 8 位地址约定 | 8-bit DevAddress Convention | HAL 的 `DevAddress` 要求已左移 1 位的 8 位字节；HAL **不代做移位**，`I2C_7BIT_ADD_WRITE/READ` 宏只调整 bit[0] | STM32 · Lesson 02.1 |
| i2c-api-selection-tree | I2C API 三分类决策 | I2C API Selection (3-class) | 按通信语义分类选 API：A 类存储空间 → `Mem_*`；B 类命令序列 → `Master_Transmit`；C 类数据流 → `Master_Receive` | STM32 · Lesson 02.1 |
| eeprom-page-write-boundary | EEPROM 页边界 | EEPROM Page Write Boundary | AT24C02 页大小 = 8 字节；单次写入跨页会**回卷**到本页起始覆盖原数据，HAL 不保护 | STM32 · Lesson 02.1 |
| eeprom-write-cycle-delay | EEPROM 写周期延迟 | EEPROM Write Cycle Delay (Twr) | AT24C02 擦写周期 ≈ 5 ms；期间芯片对任何 I2C 命令 NACK，代码须 `HAL_Delay(5)` | STM32 · Lesson 02.1 |
| oled-control-byte-co-dc | OLED 控制字节 | OLED Control Byte (Co / DC#) | SSD1306 特有协议加层；`0x00` = 后续命令流、`0x40` = 后续显存数据流 | STM32 · Lesson 02.1 |
| aht20-trigger-measure-command | AHT20 触发测量命令 | AHT20 Trigger Measure Command | 3 字节固定序列 `0xAC 0x33 0x00`，启动一次温湿度 ADC 采样 | STM32 · Lesson 02.1 |
| aht20-status-busy-bit | AHT20 busy 状态位 | AHT20 Status Busy Bit | 状态字节 bit[7]：1 = 仍在测量、0 = 完成可读；不轮询直接读得到旧数据 | STM32 · Lesson 02.1 |
| aht20-single-transaction-7byte | AHT20 单事务 7 字节读 | AHT20 Single-Transaction 7-Byte Read | 一次 `Master_Receive` 读 7 字节 = 状态(1) + 数据(5) + CRC(1)；比两次独立读高效且一并取 CRC | STM32 · Lesson 02.1 |
| crc8-aht20 | CRC-8 (AHT20) | CRC-8 Polynomial 0x31 | 多项式 `x^8+x^5+x^4+1`（0x31），初值 0xFF；AHT20 用它校验 6 字节测量数据 | STM32 · Lesson 02.1 |
| apb1-clock-i2c-lower-bound | APB1 时钟 I2C 下限 | APB1 Clock I2C Lower Bound | RM0008 §26.3.3：I2C 100 kHz 要求 APB1 ≥ 2 MHz、400 kHz 要求 ≥ 4 MHz；低于下限会静默失败 | STM32 · Lesson 02.1 |
| i2c-logic-analyzer-verification | 逻辑分析仪验证 | Logic Analyzer Verification | 用 Saleae Logic 等工具抓 SDA/SCL 波形，把 HAL 调用与实际时序对齐，排查 I2C 问题首选手段 | STM32 · Lesson 02.1 |

> 本节随课程生成逐步补录（Q5 决策：模板与 glossary 同步改造）。设计示范见 `docs/plans/2026-04-18-thinking-module-and-concept-graph-design.md` §附录 B。

---

## 使用说明

1. **按学科/主题分类维护**：新增学科时追加二级标题节，表头固定为 5 列；不要改列顺序。
2. **1:1:1 对齐**：
   - 每个 `concept_tag` 只对应一条中文关键词与一条定义
   - 跨主题同义术语应合并为同一条目，"首次出现"列填最早一次
3. **`concept_tag` 命名规范**：
   - 格式 `{topic}-{concept-name}`，全小写、连字符分隔
   - 示例：`stm32-gpio-mode`、`c-pointer-arithmetic`、`transformer-self-attention`、`adlerian-separation-of-tasks`
   - `topic` 建议取自 `roadmap_status.md` 的主题 slug 或主流学科英文简称
4. **"首次出现"格式**：`{主题名} · Lesson {N}`；若主题名较长可用缩写（如 `STM32-HAL · L3`）。
5. **新增术语的流程**（对应阶段 B 开始后的日常操作）：
   1. AI 在 `lesson-template.md` 元信息写入 `concept_tags: [...]`
   2. 同步将每个 tag 加入本表（或更新"首次出现"）
   3. 思考模块（L1）预生成关键词索引时，从本表反查中文关键词
6. **迁移策略**（与设计文档 §九 Q5 / Q7 决策一致）：
   - 旧 session 保持现状，不强制回填历史 lesson 的 concept_tag
   - 历史条目允许 `concept_tag` 列填 `—`，新增条目必须写全
7. **校验**（人工）：每季度 review 一次，查找：
   - 同一 `concept_tag` 在多行出现（违反 1:1:1）
   - `concept_tag` 命名不符格式（大写字母、下划线、空格等）
   - "首次出现"指向已不存在的 session
