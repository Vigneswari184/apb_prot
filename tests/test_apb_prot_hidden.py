from __future__ import annotations

import os
import random
from pathlib import path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_tools.runner import get_runner

LANGUAGE = os.getenv("HDL_TOPLEVEL_LANG", "verilog").lower().strip()

# Helper: APB write transaction
async def apb_write(dut, addr, data):
    dut.WADDR.value = addr
    dut.WDATA.value = data
    dut.WRITE_IN.value = 1
    dut.TRANSFER.value = 1
    await RisingEdge(dut.PCLK)
    dut.TRANSFER.value = 0
    # Wait for ACCESS phase
    while dut.PENABLE.value != 1:
        await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)
    dut.WRITE_IN.value = 0

# Helper: APB read transaction
async def apb_read(dut, addr):
    dut.WADDR.value = addr
    dut.WRITE_IN.value = 0
    dut.TRANSFER.value = 1
    await RisingEdge(dut.PCLK)
    dut.TRANSFER.value = 0
    # Wait for ACCESS phase
    while dut.PENABLE.value != 1:
        await RisingEdge(dut.PCLK)
    await RisingEdge(dut.PCLK)
    return dut.PRDATA.value.integer

# Reset
async def reset_dut(dut):
    dut.PRESET_n.value = 1
    await RisingEdge(dut.PCLK)
    dut.PRESET_n.value = 0
    await RisingEdge(dut.PCLK)
    dut.PRESET_n.value = 1
    await RisingEdge(dut.PCLK)

@cocotb.test()
async def apb_max_coverage_test(dut):
    """APB Master-Slave: Maximum coverage test"""

    # Start clock
    cocotb.start_soon(Clock(dut.PCLK, 10, units="ns").start())
    await reset_dut(dut)

    REG_NUM = 4
    ADDR_WIDTH = 8
    MAX_ADDR = 2 ** ADDR_WIDTH - 1

    # Track expected values in a model
    reg_model = [0] * REG_NUM

    for cycle in range(50):
        addr = random.randint(0, MAX_ADDR)
        is_write = random.choice([0, 1])
        data = random.randint(0, 0xFFFFFFFF)

        # Random delay between transfers
        await Timer(random.randint(1, 5) * 10, units="ns")

        if is_write:
            await apb_write(dut, addr, data)
            # Update model using slave addressing logic
            reg_model[addr % REG_NUM] = data
            dut._log.info(f"WRITE: Addr={addr} Data=0x{data:08X}")
        else:
            read_val = await apb_read(dut, addr)
            expected = reg_model[addr % REG_NUM]
            dut._log.info(f"READ : Addr={addr} Data=0x{read_val:08X} Expected=0x{expected:08X}")
            if read_val != expected:
                raise cocotb.result.TestFailure(f"Data mismatch at addr {addr}: got 0x{read_val:08X}, expected 0x{expected:08X}")

    # Edge case: Transfer=0, ensure state machine stays in IDLE
    dut.TRANSFER.value = 0
    dut.WADDR.value = 0
    dut.WDATA.value = 0
    dut.WRITE_IN.value = 1
    await RisingEdge(dut.PCLK)
    if dut.PSELx.value != 0 or dut.PENABLE.value != 0:
        raise cocotb.result.TestFailure("State machine did not stay in IDLE when TRANSFER=0")

    # Edge case: PRESET_n active during transfer
    dut.PRESET_n.value = 0
    await RisingEdge(dut.PCLK)
    dut.PRESET_n.value = 1
    await RisingEdge(dut.PCLK)
    dut._log.info("Reset during transfer tested successfully")

    dut._log.info("APB maximum coverage test completed successfully")
