<template>
    <div class="info-box">
        <i :class="'info-box-icon ion-ios-'+icon"></i>
        <div class="info-box-content">
            <span class="info-box-text"><slot></slot></span>
            <span class="info-box-number">{{count}}</span>
        </div>
    </div>
</template>
<script>
    export default{
        props: [
            /*icon: */
            'icon',
            'count'
        ]
    }
</script>
<style scroped>
    body .info-box{
        display: flex;
        min-height: 110px;
        background: #fff;
        width: 100%;
        box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        border-radius: 2px;
        margin-bottom: 15px;
        margin-right: 20px;
        position: relative;
    }
    body .info-box-icon{
        width: 60px;
        height: 60px;
        display: block;
        text-align: center;
        line-height: 60px;
        font-size: 40px;
        border-radius: 100%;
        color: #fff;
        background-color: #7CBDE8;
        position: absolute;
        top: 0;
        right: 10px;
        bottom: 0;
        margin: auto;
    }
    .info-box-content{
        flex: 1;
        padding: 5px 10%;
    }
.info-box-content span:nth-of-type(1){color:#949AA0;font-size: 12px;display: block;margin-top:12px;}
.info-box-content span:nth-of-type(2){color:#949AA0;font-size: 36px;}
    .info-box-text, .info-box-number{
        display: block;
        font-size: 14px;
    }

    .info-box-number{
        font-size: 18px;
    }

</style>