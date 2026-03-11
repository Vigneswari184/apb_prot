module apb_slave #(
    parameter ADDR_WIDTH = 8,
    parameter DATA_WIDTH = 32,
    parameter REG_NUM = 4       // Number of registers
)(
    input  wire                  PCLK,
    input  wire                  PRESET_n,
    input  wire [ADDR_WIDTH-1:0] PADDR,
    input  wire [DATA_WIDTH-1:0] PWDATA,
    input  wire                  PWRITE,
    input  wire                  PSELx,
    input  wire                  PENABLE,
    output reg  [DATA_WIDTH-1:0] PRDATA,
    output reg                   PREADY,
    output reg                   PSLVERR
);

//

endmodule
