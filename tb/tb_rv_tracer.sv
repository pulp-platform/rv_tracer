// Copyright 2025 ETH Zurich and University of Bologna.
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License.  You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
// SPDX-License-Identifier: SHL-0.51

// Author:  Umberto Laghi
// Contact: umberto.laghi2@unibo.it
// Github:  @ubolakes

`timescale 1ns/1ns

import te_pkg::*;

parameter N = 1;
parameter ONLY_BRANCHES = 1;
parameter APB_ADDR_WIDTH = 32;

module tb_rv_tracer();

    logic clk;
    logic reset;

    // inputs
    logic [N-1:0]                   valid_i;
    logic [N-1:0][ITYPE_LEN-1:0]    itype_i;
    logic [XLEN-1:0]                cause_i;
    logic [XLEN-1:0]                tval_i;
    logic [PRIV_LEN-1:0]            priv_i;
    logic [N-1:0][XLEN-1:0]         iaddr_i;
    logic [N-1:0][IRETIRE_LEN-1:0]  iretire_i;
    logic [N-1:0]                   ilastsize_i;
    logic [TIME_LEN-1:0]            time_i;
    logic [XLEN-1:0]                tvec_i;
    logic [XLEN-1:0]                epc_i;
    logic                           encapsulator_ready_i;
    logic [APB_ADDR_WIDTH-1:0]      paddr_i;
    logic                           pwrite_i;
    logic                           psel_i;
    logic                           penable_i;
    logic [31:0]                    pwdata_i;
    
    // outputs
    logic [N-1:0]                   packet_valid_o;
    it_packet_type_e [N-1:0]        packet_type_o;
    logic [N-1:0][P_LEN-1:0]        packet_length_o; // in bytes
    logic [N-1:0][PAYLOAD_LEN-1:0]  packet_payload_o;
    logic                           stall_o;
    logic                           pready_o;
    logic [31:0]                    prdata_o;

    // testing only outputs
    logic [N-1:0]                   expected_packet_valid;
    it_packet_type_e [N-1:0]        expected_packet_type;
    logic [N-1:0][P_LEN-1:0]        expected_packet_length; // in bytes
    logic [N-1:0][PAYLOAD_LEN-1:0]  expected_packet_payload;
    logic                           expected_stall;
    logic                           expected_pready;
    logic [31:0]                    expected_prdata;

    // iteration variable
    logic [31:0] i;

    rv_tracer #(
        .N(N),
        .ONLY_BRANCHES(ONLY_BRANCHES)
    ) DUT(
        .clk_i               (clk),
        .rst_ni              (reset),
        .valid_i             (valid_i),
        .itype_i             (itype_i),
        .cause_i             (cause_i),
        .tval_i              (tval_i),
        .priv_i              (priv_i),
        .iaddr_i             (iaddr_i),
        .iretire_i           (iretire_i),
        .ilastsize_i         (ilastsize_i),
        .time_i              (time_i),
        .tvec_i              (tvec_i),
        .epc_i               (epc_i),
        .encapsulator_ready_i(encapsulator_ready_i),
        .paddr_i             (paddr_i),
        .pwrite_i            (pwrite_i),
        .psel_i              (psel_i),
        .penable_i           (penable_i),
        .pwdata_i            (pwdata_i),
        .packet_valid_o      (packet_valid_o),
        .packet_type_o       (packet_type_o),
        .packet_length_o     (packet_length_o),
        .packet_payload_o    (packet_payload_o),
        .stall_o             (stall_o),
        .pready_o            (pready_o),
        .prdata_o            (prdata_o)
    );

    logic [623:0] test_vector[1000:0];

    initial begin 
        $readmemb("./tb/testvectors/tv_rv_tracer.txt", test_vector);
        i = 0;
        reset = 0; #10; // resetting for one period
        reset = 1; // set to 1 for the rest of simulation
    end

    always @(posedge clk) begin
        {
            valid_i,
            itype_i,
            cause_i,
            tval_i,
            priv_i,
            iaddr_i,
            iretire_i,
            ilastsize_i,
            time_i,
            tvec_i,
            epc_i,
            encapsulator_ready_i,
            paddr_i,
            pwrite_i,
            psel_i,
            penable_i,
            pwdata_i,
            expected_packet_valid,
            expected_packet_type,
            expected_packet_length,
            expected_packet_payload,
            expected_stall,
            expected_pready,
            expected_prdata
        } = test_vector[i]; #10;
    end

    always @(negedge clk) begin
        // packet_type_o
        if(expected_packet_type !== packet_type_o) begin
            $display("Wrong packet type: %b!=%b", expected_packet_type, packet_type_o);
        end
        // packet_length_o
        if(expected_packet_length !== packet_length_o) begin
            $display("Wrong packet length: %b!=%b", expected_packet_length, packet_length_o);
        end
        // packet_payload_o
        if(expected_packet_payload !== packet_payload_o) begin
            $display("Wrong packet payload: %b!=%b", expected_packet_payload, packet_payload_o);
        end

        // index increase
        i = i + 1;
    end

    always begin
        clk <= 1; #5;
        clk <= 0; #5;
    end

endmodule