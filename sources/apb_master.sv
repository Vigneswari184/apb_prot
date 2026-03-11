module apb_master #(
    parameter ADDR_WIDTH = 8,
    parameter DATA_WIDTH = 32
)(
    input  wire                  PCLK,
    input  wire                  PRESET_n,
    input  wire [DATA_WIDTH-1:0] PRDATA,
    input  wire                  PREADY,
    input  wire                  PSLVERR,    
    input  wire                  TRANSFER,
  	input  wire [ADDR_WIDTH-1:0] WADDR,
  	input  wire [DATA_WIDTH-1:0] WDATA,
    input  wire                  WRITE_IN,      // 1=Write, 0=Read
  	output reg  [DATA_WIDTH-1:0] RDATA,
  	output reg  [ADDR_WIDTH-1:0] PADDR,
    output reg  [DATA_WIDTH-1:0] PWDATA,
    output reg                   PWRITE,
    output reg                   PSELx,
    output reg                   PENABLE

);

 //
  
endmodule
