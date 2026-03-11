# apb_protocol
The Advanced Peripheral Bus (APB) is a simple, low-bandwidth bus protocol used to interface peripherals with a system-on-chip (SoC) master. It is part of the AMBA (Advanced Microcontroller Bus Architecture) family developed by ARM. APB is optimized for low-power, low-speed peripheral access.

**Key Features**
Simple single-cycle interface for reads and writes
Low power: no pipelining or burst transfers
Supports multiple slave devices via address decoding
Minimal handshaking signals

**APB Signals**
1. PCLK - Input	APB clock
2. PRESET_n -	Input	Active-low reset
3. PADDR -	Output	Address bus from master to slave
4. PWDATA -	Output	Write data bus from master to slave
5. PRDATA	Input	Read data bus from slave to master
6. PSELx	Output	Slave select (active high)
7. PENABLE	Output	Enable signal to indicate ACCESS phase
8. PWRITE	Output	Indicates write (1) or read (0)
9. PREADY	Input	Indicates slave ready for transfer
10. PSLVERR	Input	Indicates transfer error from slave

**APB Transfer Phases**
APB transactions are divided into two main phases:

1. SETUP Phase
  -Initiated when PSELx = 1 and PENABLE = 0.
  -Master provides the address and write data (if applicable).
  -PWRITE signal indicates the type of transfer.
  
2. ACCESS Phase
  -Initiated when PENABLE = 1.

**Data transfer occurs:**
**Write**: PWDATA is written to the selected slave register.
**Read:** Slave drives PRDATA onto the bus.

**PREADY** indicates transfer completion.
Master returns to IDLE once transfer is complete.

**State Machine (Master Side)**
    IDLE  -> SETUP  -> ACCESS  -> IDLE

**IDLE:** Waiting for a transfer request (TRANSFER=1)
**SETUP:** Prepares the address and data for the slave
**ACCESS:** Performs the actual data read/write, waits for **PREADY**

**Typical Operation**
  - Master asserts PSELx and provides address/data.
  - Master asserts PENABLE in the next cycle to enter ACCESS.

**Slave processes the transfer:**
  - Provides PRDATA for reads
  - Updates internal register for writes
  - Asserts PREADY when done
  - Master deasserts PSELx and PENABLE to return to IDLE.

**Advantages**
  - Simple interface reduces design complexity.
  - Low power due to no pipelining.
  - Suitable for control/status registers in peripherals.
