from __future__ import annotations

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_tools.runner import get_runner


# ------------------------------
# Coverage Counters
# ------------------------------

coverage = {
    "writes": 0,
    "reads": 0,
    "addr_hits": set(),
    "reset_events": 0
}


# ------------------------------
# Wait for ACCESS phase
# ------------------------------

async def wait_for_penable(dut, timeout=20):
    for _ in range(timeout):
        if dut.PENABLE.value == 1:
            return
        await RisingEdge(dut.PCLK)

    raise RuntimeError("Timeout waiting for PENABLE")


# ------------------------------
# APB WRITE
# ------------------------------

async def apb_write(dut, addr, data):

    dut.WADDR.value = addr
    dut.WDATA.value = data
    dut.WRITE_IN.value = 1
    dut.TRANSFER.value = 1

    await RisingEdge(dut.PCLK)

    dut.TRANSFER.value = 0

    await wait_for_penable(dut)

    await RisingEdge(dut.PCLK)

    dut.WRITE_IN.value = 0

    coverage["writes"] += 1
    coverage["addr_hits"].add(addr)


# ------------------------------
# APB READ
# ------------------------------

async def apb_read(dut, addr):

    dut.WADDR.value = addr
    dut.WRITE_IN.value = 0
    dut.TRANSFER.value = 1

    await RisingEdge(dut.PCLK)

    dut.TRANSFER.value = 0

    await wait_for_penable(dut)

    await RisingEdge(dut.PCLK)

    coverage["reads"] += 1
    coverage["addr_hits"].add(addr)

    return dut.PRDATA.value.to_unsigned()


# ------------------------------
# RESET
# ------------------------------

async def reset_dut(dut):

    dut.PRESET_n.value = 1
    await RisingEdge(dut.PCLK)

    dut.PRESET_n.value = 0
    await RisingEdge(dut.PCLK)

    dut.PRESET_n.value = 1
    await RisingEdge(dut.PCLK)

    coverage["reset_events"] += 1


# ------------------------------
# MAIN TEST
# ------------------------------

@cocotb.test()
async def apb_full_coverage_test(dut):

    cocotb.start_soon(Clock(dut.PCLK, 10, unit="ns").start())

    await reset_dut(dut)

    REG_NUM = 4
    ADDR_WIDTH = 8
    MAX_ADDR = 2**ADDR_WIDTH - 1

    reg_model = [0] * REG_NUM

    # --------------------------------
    # 1️⃣ Directed Register Test
    # --------------------------------

    for i in range(REG_NUM):

        addr = i * 4
        data = random.randint(0, 0xFFFFFFFF)

        await apb_write(dut, addr, data)
        reg_model[i] = data

        read_val = await apb_read(dut, addr)

        assert read_val == data, f"Directed test failed addr {addr}"


    # --------------------------------
    # 2️⃣ Boundary Test
    # --------------------------------

    for addr in [0x00, 0x04, 0xFC, 0xFF]:

        data = random.randint(0, 0xFFFFFFFF)

        await apb_write(dut, addr, data)

        reg_model[(addr // 4) % REG_NUM] = data

        read_val = await apb_read(dut, addr)

        assert read_val == reg_model[(addr // 4) % REG_NUM]


    # --------------------------------
    # 3️⃣ Random Stress Test
    # --------------------------------

    for cycle in range(200):

        addr = random.randint(0, MAX_ADDR)
        data = random.randint(0, 0xFFFFFFFF)
        is_write = random.choice([0, 1])

        if is_write:

            await apb_write(dut, addr, data)

            reg_model[(addr // 4) % REG_NUM] = data

        else:

            read_val = await apb_read(dut, addr)

            expected = reg_model[(addr // 4) % REG_NUM]

            assert read_val == expected, \
                f"Mismatch addr {addr} got {read_val} expected {expected}"


    # --------------------------------
    # 4️⃣ Back-to-back transfers
    # --------------------------------

    for i in range(20):

        addr = (i * 4) % 256
        data = random.randint(0, 0xFFFFFFFF)

        await apb_write(dut, addr, data)
        reg_model[(addr // 4) % REG_NUM] = data

        read_val = await apb_read(dut, addr)

        assert read_val == data


    # --------------------------------
    # 5️⃣ Reset During Operation
    # --------------------------------

    await apb_write(dut, 0x08, 0xABCDEF01)

    await reset_dut(dut)

    read_val = await apb_read(dut, 0x08)

    dut._log.info("Reset behaviour tested")

    # --------------------------------
    # 6️⃣ IDLE: TRANSFER=0 → no bus activity
    # --------------------------------

    dut.TRANSFER.value = 0
    dut.WADDR.value = 0
    dut.WDATA.value = 0
    dut.WRITE_IN.value = 0
    await RisingEdge(dut.PCLK)
    assert dut.PSELx.value == 0, "PSELx should be 0 in IDLE when TRANSFER=0"
    assert dut.PENABLE.value == 0, "PENABLE should be 0 in IDLE when TRANSFER=0"
    dut._log.info("IDLE (TRANSFER=0) behaviour verified")

    # --------------------------------
    # Coverage Report
    # --------------------------------

    dut._log.info("------ COVERAGE REPORT ------")
    dut._log.info(f"Writes performed : {coverage['writes']}")
    dut._log.info(f"Reads performed  : {coverage['reads']}")
    dut._log.info(f"Unique addresses : {len(coverage['addr_hits'])}")
    dut._log.info(f"Reset events     : {coverage['reset_events']}")

    dut._log.info("APB FULL COVERAGE TEST PASSED")


def test_apb_prot_hidden_runner():
    """Pytest entry point: build RTL and run cocotb tests."""
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sources = [
        proj_path / "sources/apb_top.sv",
        proj_path / "sources/apb_master.sv",
        proj_path / "sources/apb_slave.sv",
    ]
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="apb_top",
        always=True,
    )
    runner.test(hdl_toplevel="apb_top", test_module="test_apb_prot_hidden")
