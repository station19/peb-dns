<template>
    <div class="top-counter-wrap">
        <counter icon="gear-outline" :count="countData.server_amount" class="server-count">服务器总数</counter>
        <counter icon="grid-view" :count="countData.view_amount" class="view-count">VIEW总数</counter>
        <counter icon="cart-outline" :count="countData.zone_amount" class="zone-count">ZONE总数</counter>
        <counter icon="recording" :count="countData.record_amount" class="record-count">记录总数</counter>

    </div>
</template>
<script>
    import counter from './counter.vue';
    import Ajax from 'ajax';
    let counterAjax = new Ajax();
    export default {
        data(){
            return {
                countData: {
                    record_amount: '',
                    server_amount: '',
                    view_amount: '',
                    zone_amount: ''
                }
                
            }       
        },
        mounted() {
            let self = this;
            counterAjax.get({
                url: 'http://hfdns-test.ipo.com/page/resource_amount',
                success(response){
                    self.countData = response.data;
                }
            });
        },
        components:{
            counter: counter
        }
    }
</script>
