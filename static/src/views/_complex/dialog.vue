<template>
    <div>
        <transition name="slidetop">
            <div class="modal" id="modal-default" v-show="isShow">
                <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                          <span aria-hidden="true" @click="isShow = false">×</span></button>
                        <h4 class="modal-title">{{ title }}</h4>
                      </div>
                      <div class="modal-body">
                            <slot></slot>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-default" data-dismiss="modal" @click="hide">关闭</button>
                        <button type="button" class="btn btn-primary" @click="$emit('dialog:save')">保存</button>
                      </div>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>
<script>
    import {Overlay, Mask} from 'vpui';
    export default {
        data(){
            return {
                isShow: false
            }
        },
        components: {
            overlay: Overlay,
            vpMask: Mask,
        },
        props : {
            title: {
                type: String,
                default: '创建记录：'
            }
        },
        methods: {
            show(){
                this.isShow = true;
            },
            hide(){
                this.isShow = false;
            }
        }
    }
</script>
<style scoped>
    #modal-default{
        overflow:auto;
    }
    .modal{
        display: block;
    }
    .dialog-title{
        text-align: center;
        font-size: 18px;
    }

    .dialog-window{
        width: 346px;
        height: 384px;
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        margin: auto;
        border-radius: 10px;
    }

    .dialog-content{
        padding-top: 40px;
        text-align: center;
        background-color: #fff;
        height: 235px;
        border-radius: 3px;
        border-top-left-radius: 0;
    }
    

    .dialog-input,.dialog-password-helper{
        display: block;
        width: 305px;
        height: 36px;
        margin: 0 auto;
        margin-bottom: 8px;
        background: #F5FAFE;
        border: 1px solid #72BFF0;
        border-radius: 4px;
        padding: 3px;
        padding: 12px 35px 12px 12px;
        color: #69B8EA;
    }

    .dialog-password-helper{
        height: auto;
        padding: 0;
        border: 0;
        background: transparent;
        text-align: left;
        font-weight: normal;
    }

    .dialog-password-helper input[type="checkbox"]{
        display: inline-block;
        vertical-align: middle;
        margin: 0;
        margin-right: 10px;
    }


    .dialog-password-helper label{
        font-weight: normal;
        line-height: 24px;
        height: 24px;
        font-size: 12px;
    }

    .find-paddword{
        float: right;
    }
    
    .input-label{
        display:inline-block;
        width: 80px;
        text-align: right;
    }
    .project-name{
        position: absolute;
        top: 20px;
        right: 30px;
        opacity: 0.9;
        font-family: PingFangSC-Medium;
        font-size: 30px;
        color: #FFFFFF;
    }
    .dialog-btn{
        width: 306px;
        height: 40px;
        background-color: #72BFF0;
        color:#fff;
        border: 0;
    }
    .dialog-title-item{
        background-color: #fff;
        height: 50px;
        line-height: 50px;
        width: 160px;
        color: #72BFF0;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }

    .slidetop-enter-active{
        transition: all .3s ease;
    }

    .slidetop-enter .modal-dialog{
        opacity: 0;
        transform: translateY(-500px);
    }

    .slidetop-enter-to .modal-dialog{
        transition: all .3s ease;
        transform: translateY(0);
        opacity: 1;
    }

    .slidetop-leave-active{
        transition: all .3s ease;
    }
    
    .slidetop-leave-to .modal-dialog{
        transition: all .3s ease;
        transform: translateY(-500px);
        opacity: 0;
    }

</style>