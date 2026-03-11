`timescale 1ns/1ps

module apb_top #(
    parameter ADDR_WIDTH = 8,
    parameter DATA_WIDTH = 32,
    parameter REG_NUM    = 4
)(
    input  wire                  PCLK,
    input  wire                  PRESET_n,
    input  wire                  TRANSFER,
    input  wire [ADDR_WIDTH-1:0] WADDR,
    input  wire [DATA_WIDTH-1:0] WDATA,
    input  wire                  WRITE_IN,
    output wire [DATA_WIDTH-1:0] PRDATA,
    output wire                  PSELx,
    output wire                  PENABLE
);
    // APB bus between master and slave
    wire [ADDR_WIDTH-1:0] PADDR;
    wire [DATA_WIDTH-1:0] PWDATA;
    wire                  PWRITE;
    wire                  PREADY;
    wire                  PSLVERR;

    apb_master #(
        .ADDR_WIDTH ( ADDR_WIDTH ),
        .DATA_WIDTH ( DATA_WIDTH )
    ) u_master (
        .PCLK     ( PCLK     ),
        .PRESET_n ( PRESET_n ),
        .PRDATA   ( PRDATA   ),
        .PREADY   ( PREADY   ),
        .PSLVERR  ( PSLVERR  ),
        .TRANSFER ( TRANSFER ),
        .WADDR    ( WADDR    ),
        .WDATA    ( WDATA    ),
        .WRITE_IN ( WRITE_IN ),
        .PADDR    ( PADDR    ),
        .PWDATA   ( PWDATA   ),
        .PWRITE   ( PWRITE   ),
        .PSELx    ( PSELx    ),
        .PENABLE  ( PENABLE  )
    );

    apb_slave #(
        .ADDR_WIDTH ( ADDR_WIDTH ),
        .DATA_WIDTH ( DATA_WIDTH ),
        .REG_NUM    ( REG_NUM   )
    ) u_slave (
        .PCLK     ( PCLK     ),
        .PRESET_n ( PRESET_n ),
        .PADDR    ( PADDR    ),
        .PWDATA   ( PWDATA   ),
        .PWRITE   ( PWRITE   ),
        .PSELx    ( PSELx    ),
        .PENABLE  ( PENABLE  ),
        .PRDATA   ( PRDATA   ),
        .PREADY   ( PREADY   ),
        .PSLVERR  ( PSLVERR  )
    );
endmodule
