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

  typedef enum logic [1:0] {IDLE, SETUP, ACCESS} state_t;
state_t state;
  reg [1:0] present,next;

  always @(posedge PCLK or posedge PRESET_n) begin
    if (PRESET_n)
      present <= IDLE;
    else
      present <= next;
  end
       
  always @(*) begin    
    case(present)        
        IDLE: begin
          PSELx = 0;
          PENABLE = 0;
          PADDR = 0;
          PWDATA = 0;
          if(TRANSFER == 1)
            begin
              next = SETUP;
            end
          else
              next = IDLE;
          end          
        
        SETUP: begin
          PSELx = 1;
          PENABLE = 0;
          if(WRITE_IN==1)
            begin
              next = ACCESS;
              PADDR = WADDR;
              PWDATA = WDATA;
              PWRITE = WRITE_IN;
            end
        end                      
         ACCESS: begin
           PSELx = 1;
           PENABLE = 1;
           if(PREADY == 0)
             next = ACCESS;
           else if(PREADY==1 && WRITE_IN)
             begin
               next = IDLE;
               PADDR = WADDR;
               PWDATA = WDATA;
               PWRITE = WRITE_IN;
              end
          else
              next = IDLE;           
         end          
          endcase          
        end
  
endmodule
