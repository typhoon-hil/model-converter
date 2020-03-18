// generated using template: cop_main.template---------------------------------------------
/******************************************************************************************
**
**  Module Name: cop_main.c
**  NOTE: Automatically generated file. DO NOT MODIFY!
**  Description:
**            Main file
**
******************************************************************************************/
// generated using template: arm/custom_include.template-----------------------------------

// x86 libraries:
#include "../include/sp_functions_dev0.h"

// H files from Advanced C Function components
//#include "example_dll.h"

// Header files from additional sources (Advanced C Function)
// ----------------------------------------------------------------------------------------
// generated using template: VirtualHIL/custom_defines.template----------------------------

typedef unsigned char X_UnInt8;
typedef char X_Int8;
typedef signed short X_Int16;
typedef unsigned short X_UnInt16;
typedef int X_Int32;
typedef unsigned int X_UnInt32;
typedef unsigned int uint;
typedef double real;

// ----------------------------------------------------------------------------------------
// generated using template: custom_consts.template----------------------------------------

// arithmetic constants
#define C_SQRT_2                    1.4142135623730950488016887242097f
#define C_SQRT_3                    1.7320508075688772935274463415059f
#define C_PI                        3.1415926535897932384626433832795f
#define C_E                         2.7182818284590452353602874713527f
#define C_2PI                       6.283185307179586476925286766559f

//@cmp.def.start
//component defines


































































//@cmp.def.end


//-----------------------------------------------------------------------------------------
// generated using template: common_variables.template-------------------------------------
// true global variables


//@cmp.var.start
// variables
float _il2_iinst_ia1__out;
float _il3_iinst_ia1__out;
float _vc2_vinst_va1__out;
float _vc3_vinst_va1__out;
float _vc_el2_vinst_va1__out;
float _vc_el3_vinst_va1__out;
float _il2_rms_calc_fast__var_eff_s;
X_UnInt32 _il2_rms_calc_fast__period;
float _il2_rms_calc_slow__var_rms;
float _il3_rms_calc_fast__var_eff_s;
X_UnInt32 _il3_rms_calc_fast__period;
float _il3_rms_calc_slow__var_rms;
float _vc2_rms_calc_fast__var_eff_s;
X_UnInt32 _vc2_rms_calc_fast__period;
float _vc2_rms_calc_slow__var_rms;
float _vc3_rms_calc_fast__var_eff_s;
X_UnInt32 _vc3_rms_calc_fast__period;
float _vc3_rms_calc_slow__var_rms;
float _vc_el2_rms_calc_fast__var_eff_s;
X_UnInt32 _vc_el2_rms_calc_fast__period;
float _vc_el2_rms_calc_slow__var_rms;
float _vc_el3_rms_calc_fast__var_eff_s;
X_UnInt32 _vc_el3_rms_calc_fast__period;
float _vc_el3_rms_calc_slow__var_rms;
//@cmp.var.end

//@cmp.svar.start
// state variables
float _il2_rt1_output__out =  0.0;

float _il2_rt2_output__out =  0.0;

float _il3_rt1_output__out =  0.0;

float _il3_rt2_output__out =  0.0;

float _vc2_rt1_output__out =  0.0;

float _vc2_rt2_output__out =  0.0;

float _vc3_rt1_output__out =  0.0;

float _vc3_rt2_output__out =  0.0;

float _vc_el2_rt1_output__out =  0.0;

float _vc_el2_rt2_output__out =  0.0;

float _vc_el3_rt1_output__out =  0.0;

float _vc_el3_rt2_output__out =  0.0;

float _il2_rms_calc_fast__v_sq_sum_state;
X_UnInt32 _il2_rms_calc_fast__pc_cnt_1_state;
float _il2_rms_calc_fast__var_filt;
float _il3_rms_calc_fast__v_sq_sum_state;
X_UnInt32 _il3_rms_calc_fast__pc_cnt_1_state;
float _il3_rms_calc_fast__var_filt;
float _vc2_rms_calc_fast__v_sq_sum_state;
X_UnInt32 _vc2_rms_calc_fast__pc_cnt_1_state;
float _vc2_rms_calc_fast__var_filt;
float _vc3_rms_calc_fast__v_sq_sum_state;
X_UnInt32 _vc3_rms_calc_fast__pc_cnt_1_state;
float _vc3_rms_calc_fast__var_filt;
float _vc_el2_rms_calc_fast__v_sq_sum_state;
X_UnInt32 _vc_el2_rms_calc_fast__pc_cnt_1_state;
float _vc_el2_rms_calc_fast__var_filt;
float _vc_el3_rms_calc_fast__v_sq_sum_state;
X_UnInt32 _vc_el3_rms_calc_fast__pc_cnt_1_state;
float _vc_el3_rms_calc_fast__var_filt;
//@cmp.svar.end
// generated using template: virtual_hil/custom_functions.template---------------------------------
void ReInit_sys_sp_cpu_dev0() {
#if DEBUG_MODE
    printf("\n\rReInitTimer");
#endif
    //@cmp.init.block.start
    _il2_rt1_output__out =  0.0;
    _il2_rt2_output__out =  0.0;
    _il3_rt1_output__out =  0.0;
    _il3_rt2_output__out =  0.0;
    _vc2_rt1_output__out =  0.0;
    _vc2_rt2_output__out =  0.0;
    _vc3_rt1_output__out =  0.0;
    _vc3_rt2_output__out =  0.0;
    _vc_el2_rt1_output__out =  0.0;
    _vc_el2_rt2_output__out =  0.0;
    _vc_el3_rt1_output__out =  0.0;
    _vc_el3_rt2_output__out =  0.0;
    _il2_rms_calc_fast__var_eff_s = 0;
    _il2_rms_calc_fast__period = 0;
    _il2_rms_calc_fast__var_filt = 0.0f;
    _il2_rms_calc_fast__v_sq_sum_state = 0.0f;
    _il2_rms_calc_fast__pc_cnt_1_state = 0;
    _il3_rms_calc_fast__var_eff_s = 0;
    _il3_rms_calc_fast__period = 0;
    _il3_rms_calc_fast__var_filt = 0.0f;
    _il3_rms_calc_fast__v_sq_sum_state = 0.0f;
    _il3_rms_calc_fast__pc_cnt_1_state = 0;
    _vc2_rms_calc_fast__var_eff_s = 0;
    _vc2_rms_calc_fast__period = 0;
    _vc2_rms_calc_fast__var_filt = 0.0f;
    _vc2_rms_calc_fast__v_sq_sum_state = 0.0f;
    _vc2_rms_calc_fast__pc_cnt_1_state = 0;
    _vc3_rms_calc_fast__var_eff_s = 0;
    _vc3_rms_calc_fast__period = 0;
    _vc3_rms_calc_fast__var_filt = 0.0f;
    _vc3_rms_calc_fast__v_sq_sum_state = 0.0f;
    _vc3_rms_calc_fast__pc_cnt_1_state = 0;
    _vc_el2_rms_calc_fast__var_eff_s = 0;
    _vc_el2_rms_calc_fast__period = 0;
    _vc_el2_rms_calc_fast__var_filt = 0.0f;
    _vc_el2_rms_calc_fast__v_sq_sum_state = 0.0f;
    _vc_el2_rms_calc_fast__pc_cnt_1_state = 0;
    _vc_el3_rms_calc_fast__var_eff_s = 0;
    _vc_el3_rms_calc_fast__period = 0;
    _vc_el3_rms_calc_fast__var_filt = 0.0f;
    _vc_el3_rms_calc_fast__v_sq_sum_state = 0.0f;
    _vc_el3_rms_calc_fast__pc_cnt_1_state = 0;
    HIL_OutAO(0x4000, 0.0f);
    HIL_OutAO(0x4001, 0.0f);
    HIL_OutAO(0x4002, 0.0f);
    HIL_OutAO(0x4003, 0.0f);
    HIL_OutAO(0x4004, 0.0f);
    HIL_OutAO(0x4005, 0.0f);
    //@cmp.init.block.end
}

void ReInit_sp_scope_sys_sp_cpu_dev0() {
    // initialise SP Scope buffer pointer
}
// generated using template: common_timer_counter_handler.template-------------------------

/*****************************************************************************************/
/**
* This function is the handler which performs processing for the timer counter.
* It is called from an interrupt context such that the amount of processing
* performed should be minimized.  It is called when the timer counter expires
* if interrupts are enabled.
*
*
* @param    None
*
* @return   None
*
* @note     None
*
*****************************************************************************************/

void TimerCounterHandler_0_sys_sp_cpu_dev0() {
#if DEBUG_MODE
    printf("\n\rTimerCounterHandler_0");
#endif
    //////////////////////////////////////////////////////////////////////////
    // Output block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.out.block.start
    // Generated from the component: IL2.Iinst.Ia1
    _il2_iinst_ia1__out = (HIL_InFloat(0xc80000 + 0x604));
    // Generated from the component: IL3.Iinst.Ia1
    _il3_iinst_ia1__out = (HIL_InFloat(0xc80000 + 0x605));
    // Generated from the component: VC2.Vinst.Va1
    _vc2_vinst_va1__out = (HIL_InFloat(0xc80000 + 0x4));
    // Generated from the component: VC3.Vinst.Va1
    _vc3_vinst_va1__out = (HIL_InFloat(0xc80000 + 0x5));
    // Generated from the component: VC_el2.Vinst.Va1
    _vc_el2_vinst_va1__out = (HIL_InFloat(0xc80000 + 0x204));
    // Generated from the component: VC_el3.Vinst.Va1
    _vc_el3_vinst_va1__out = (HIL_InFloat(0xc80000 + 0x205));
    // Generated from the component: IL2.rms_calc_fast
    _il2_rms_calc_fast__v_sq_sum_state = _il2_rms_calc_fast__v_sq_sum_state + _il2_iinst_ia1__out * _il2_iinst_ia1__out;
    //square sum and period update on period end
    if (200 == _il2_rms_calc_fast__pc_cnt_1_state) {
        _il2_rms_calc_fast__var_eff_s = _il2_rms_calc_fast__v_sq_sum_state;
        _il2_rms_calc_fast__period = (float)200;
        _il2_rms_calc_fast__v_sq_sum_state = 0.0f;
    }
    // Generated from the component: IL2.sys1
    // Generated from the component: IL3.rms_calc_fast
    _il3_rms_calc_fast__v_sq_sum_state = _il3_rms_calc_fast__v_sq_sum_state + _il3_iinst_ia1__out * _il3_iinst_ia1__out;
    //square sum and period update on period end
    if (200 == _il3_rms_calc_fast__pc_cnt_1_state) {
        _il3_rms_calc_fast__var_eff_s = _il3_rms_calc_fast__v_sq_sum_state;
        _il3_rms_calc_fast__period = (float)200;
        _il3_rms_calc_fast__v_sq_sum_state = 0.0f;
    }
    // Generated from the component: IL3.sys1
    // Generated from the component: VC2.rms_calc_fast
    _vc2_rms_calc_fast__v_sq_sum_state = _vc2_rms_calc_fast__v_sq_sum_state + _vc2_vinst_va1__out * _vc2_vinst_va1__out;
    //square sum and period update on period end
    if (200 == _vc2_rms_calc_fast__pc_cnt_1_state) {
        _vc2_rms_calc_fast__var_eff_s = _vc2_rms_calc_fast__v_sq_sum_state;
        _vc2_rms_calc_fast__period = (float)200;
        _vc2_rms_calc_fast__v_sq_sum_state = 0.0f;
    }
    // Generated from the component: VC2.sys1
    // Generated from the component: VC3.rms_calc_fast
    _vc3_rms_calc_fast__v_sq_sum_state = _vc3_rms_calc_fast__v_sq_sum_state + _vc3_vinst_va1__out * _vc3_vinst_va1__out;
    //square sum and period update on period end
    if (200 == _vc3_rms_calc_fast__pc_cnt_1_state) {
        _vc3_rms_calc_fast__var_eff_s = _vc3_rms_calc_fast__v_sq_sum_state;
        _vc3_rms_calc_fast__period = (float)200;
        _vc3_rms_calc_fast__v_sq_sum_state = 0.0f;
    }
    // Generated from the component: VC3.sys1
    // Generated from the component: VC_el2.rms_calc_fast
    _vc_el2_rms_calc_fast__v_sq_sum_state = _vc_el2_rms_calc_fast__v_sq_sum_state + _vc_el2_vinst_va1__out * _vc_el2_vinst_va1__out;
    //square sum and period update on period end
    if (200 == _vc_el2_rms_calc_fast__pc_cnt_1_state) {
        _vc_el2_rms_calc_fast__var_eff_s = _vc_el2_rms_calc_fast__v_sq_sum_state;
        _vc_el2_rms_calc_fast__period = (float)200;
        _vc_el2_rms_calc_fast__v_sq_sum_state = 0.0f;
    }
    // Generated from the component: VC_el2.sys1
    // Generated from the component: VC_el3.rms_calc_fast
    _vc_el3_rms_calc_fast__v_sq_sum_state = _vc_el3_rms_calc_fast__v_sq_sum_state + _vc_el3_vinst_va1__out * _vc_el3_vinst_va1__out;
    //square sum and period update on period end
    if (200 == _vc_el3_rms_calc_fast__pc_cnt_1_state) {
        _vc_el3_rms_calc_fast__var_eff_s = _vc_el3_rms_calc_fast__v_sq_sum_state;
        _vc_el3_rms_calc_fast__period = (float)200;
        _vc_el3_rms_calc_fast__v_sq_sum_state = 0.0f;
    }
    // Generated from the component: VC_el3.sys1
    // Generated from the component: IL2.rt1.Input
    _il2_rt1_output__out = _il2_rms_calc_fast__var_eff_s;
    // Generated from the component: IL2.rt2.Input
    _il2_rt2_output__out = _il2_rms_calc_fast__period;
    // Generated from the component: IL2.t1
    // Generated from the component: IL3.rt1.Input
    _il3_rt1_output__out = _il3_rms_calc_fast__var_eff_s;
    // Generated from the component: IL3.rt2.Input
    _il3_rt2_output__out = _il3_rms_calc_fast__period;
    // Generated from the component: IL3.t1
    // Generated from the component: VC2.rt1.Input
    _vc2_rt1_output__out = _vc2_rms_calc_fast__var_eff_s;
    // Generated from the component: VC2.rt2.Input
    _vc2_rt2_output__out = _vc2_rms_calc_fast__period;
    // Generated from the component: VC2.t1
    // Generated from the component: VC3.rt1.Input
    _vc3_rt1_output__out = _vc3_rms_calc_fast__var_eff_s;
    // Generated from the component: VC3.rt2.Input
    _vc3_rt2_output__out = _vc3_rms_calc_fast__period;
    // Generated from the component: VC3.t1
    // Generated from the component: VC_el2.rt1.Input
    _vc_el2_rt1_output__out = _vc_el2_rms_calc_fast__var_eff_s;
    // Generated from the component: VC_el2.rt2.Input
    _vc_el2_rt2_output__out = _vc_el2_rms_calc_fast__period;
    // Generated from the component: VC_el2.t1
    // Generated from the component: VC_el3.rt1.Input
    _vc_el3_rt1_output__out = _vc_el3_rms_calc_fast__var_eff_s;
    // Generated from the component: VC_el3.rt2.Input
    _vc_el3_rt2_output__out = _vc_el3_rms_calc_fast__period;
    // Generated from the component: VC_el3.t1
    //@cmp.out.block.end
    //////////////////////////////////////////////////////////////////////////
    // Update block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.update.block.start
    // Generated from the component: IL2.rms_calc_fast
    if (200 == _il2_rms_calc_fast__pc_cnt_1_state) {
        _il2_rms_calc_fast__pc_cnt_1_state = 0;
    }
    _il2_rms_calc_fast__pc_cnt_1_state ++;
    // Generated from the component: IL3.rms_calc_fast
    if (200 == _il3_rms_calc_fast__pc_cnt_1_state) {
        _il3_rms_calc_fast__pc_cnt_1_state = 0;
    }
    _il3_rms_calc_fast__pc_cnt_1_state ++;
    // Generated from the component: VC2.rms_calc_fast
    if (200 == _vc2_rms_calc_fast__pc_cnt_1_state) {
        _vc2_rms_calc_fast__pc_cnt_1_state = 0;
    }
    _vc2_rms_calc_fast__pc_cnt_1_state ++;
    // Generated from the component: VC3.rms_calc_fast
    if (200 == _vc3_rms_calc_fast__pc_cnt_1_state) {
        _vc3_rms_calc_fast__pc_cnt_1_state = 0;
    }
    _vc3_rms_calc_fast__pc_cnt_1_state ++;
    // Generated from the component: VC_el2.rms_calc_fast
    if (200 == _vc_el2_rms_calc_fast__pc_cnt_1_state) {
        _vc_el2_rms_calc_fast__pc_cnt_1_state = 0;
    }
    _vc_el2_rms_calc_fast__pc_cnt_1_state ++;
    // Generated from the component: VC_el3.rms_calc_fast
    if (200 == _vc_el3_rms_calc_fast__pc_cnt_1_state) {
        _vc_el3_rms_calc_fast__pc_cnt_1_state = 0;
    }
    _vc_el3_rms_calc_fast__pc_cnt_1_state ++;
    //@cmp.update.block.end
}
void TimerCounterHandler_1_sys_sp_cpu_dev0() {
#if DEBUG_MODE
    printf("\n\rTimerCounterHandler_1");
#endif
    //////////////////////////////////////////////////////////////////////////
    // Output block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.out.block.start
    // Generated from the component: IL2.rt1.Output
    // Generated from the component: IL2.rt2.Output
    // Generated from the component: IL3.rt1.Output
    // Generated from the component: IL3.rt2.Output
    // Generated from the component: VC2.rt1.Output
    // Generated from the component: VC2.rt2.Output
    // Generated from the component: VC3.rt1.Output
    // Generated from the component: VC3.rt2.Output
    // Generated from the component: VC_el2.rt1.Output
    // Generated from the component: VC_el2.rt2.Output
    // Generated from the component: VC_el3.rt1.Output
    // Generated from the component: VC_el3.rt2.Output
    // Generated from the component: IL2.rms_calc_slow
    if(_il2_rt2_output__out > 0.0f) {
        _il2_rms_calc_slow__var_rms = sqrtf(_il2_rt1_output__out / _il2_rt2_output__out);
    }
    else {
        _il2_rms_calc_slow__var_rms = 0.0f;
    }
    // Generated from the component: IL3.rms_calc_slow
    if(_il3_rt2_output__out > 0.0f) {
        _il3_rms_calc_slow__var_rms = sqrtf(_il3_rt1_output__out / _il3_rt2_output__out);
    }
    else {
        _il3_rms_calc_slow__var_rms = 0.0f;
    }
    // Generated from the component: VC2.rms_calc_slow
    if(_vc2_rt2_output__out > 0.0f) {
        _vc2_rms_calc_slow__var_rms = sqrtf(_vc2_rt1_output__out / _vc2_rt2_output__out);
    }
    else {
        _vc2_rms_calc_slow__var_rms = 0.0f;
    }
    // Generated from the component: VC3.rms_calc_slow
    if(_vc3_rt2_output__out > 0.0f) {
        _vc3_rms_calc_slow__var_rms = sqrtf(_vc3_rt1_output__out / _vc3_rt2_output__out);
    }
    else {
        _vc3_rms_calc_slow__var_rms = 0.0f;
    }
    // Generated from the component: VC_el2.rms_calc_slow
    if(_vc_el2_rt2_output__out > 0.0f) {
        _vc_el2_rms_calc_slow__var_rms = sqrtf(_vc_el2_rt1_output__out / _vc_el2_rt2_output__out);
    }
    else {
        _vc_el2_rms_calc_slow__var_rms = 0.0f;
    }
    // Generated from the component: VC_el3.rms_calc_slow
    if(_vc_el3_rt2_output__out > 0.0f) {
        _vc_el3_rms_calc_slow__var_rms = sqrtf(_vc_el3_rt1_output__out / _vc_el3_rt2_output__out);
    }
    else {
        _vc_el3_rms_calc_slow__var_rms = 0.0f;
    }
    // Generated from the component: IL2.rms
    HIL_OutAO(0x4000, _il2_rms_calc_slow__var_rms);
    // Generated from the component: IL2.sys2
    // Generated from the component: IL3.rms
    HIL_OutAO(0x4001, _il3_rms_calc_slow__var_rms);
    // Generated from the component: IL3.sys2
    // Generated from the component: VC2.rms
    HIL_OutAO(0x4002, _vc2_rms_calc_slow__var_rms);
    // Generated from the component: VC2.sys2
    // Generated from the component: VC3.rms
    HIL_OutAO(0x4003, _vc3_rms_calc_slow__var_rms);
    // Generated from the component: VC3.sys2
    // Generated from the component: VC_el2.rms
    HIL_OutAO(0x4004, _vc_el2_rms_calc_slow__var_rms);
    // Generated from the component: VC_el2.sys2
    // Generated from the component: VC_el3.rms
    HIL_OutAO(0x4005, _vc_el3_rms_calc_slow__var_rms);
    // Generated from the component: VC_el3.sys2
    //@cmp.out.block.end
    //////////////////////////////////////////////////////////////////////////
    // Update block
    //////////////////////////////////////////////////////////////////////////
    //@cmp.update.block.start
    //@cmp.update.block.end
}
// ----------------------------------------------------------------------------------------  //-----------------------------------------------------------------------------------------