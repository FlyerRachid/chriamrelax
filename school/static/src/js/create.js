//alert('Odoo Js <+> ..*.. <+>');

data = []

function generateToken() {

      var pass = '';
      var str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
              'abcdefghijklmnopqrstuvwxyz0123456789@#$';
      for (i = 1; i <= 30; i++) {
          var char = Math.floor(Math.random()
                      * str.length + 1);

          pass += str.charAt(char)
      }
      return pass;
    }


function open_modalRequest(info) {
  document.getElementById('btn_modalRequest').click();
  data = []
  var token = info.event.extendedProps.token
  data.push(token);
  console.log(data);
  /*
  console.log('Data ',info.event.extendedProps);
  console.log(info.event.start.toLocaleDateString());
  var fdate = info.event.start.toLocaleString("fr-FR", {day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'})
  console.log(fdate);
  var system_id    =  info.event.extendedProps.system_id;
  var residence_id =  info.event.extendedProps.residence_id;
  data.push(system_id);
  data.push(residence_id);
  console.log(data)
  */
}



function sendRequest(info) {
    
      alert("Sending request ....",data[0]);
      /*
      var outpute    = obj.getElementsByTagName('INPUT');
      var token      = outpute[0].value;
      var message    = document.getElementById('message_med');
      message.value  = "";
      var tokenMsg   = document.getElementById('tokenMsg');
      tokenMsg.value = token;
      var outpute    = obj.getElementsByTagName('INPUT');
      var token      = outpute[0].value;
      var index      = sum.findIndex(function(obj) {return obj[0][0] == token;})
      console.log(index);
      const tab      = sum[index];
      console.log(tab[0][7])
      if (tab[0][7] != 'M.N.R'){
          message.value = tab[0][7];
      }
      return false;
      tab[0].push("message")
      const doseTime = tab.slice(1, tab.length);
      */
      
    
      var formData = new FormData();
      var http     = new XMLHttpRequest();

      const tab = data;

      var token = tab[0];
    
      formData.append('token'   ,token);
      
      console.log(formData);

      http.open('POST', '/request', true);

      http.onreadystatechange = function() {
          if((http.status == 200) && (http.readyState == 4)) {
              
           var json = JSON.parse(http.responseText);
           
           if (json.error == true){
               console.log('ERROR : ',json.error);
            
           }else if(json.error == false){
                 console.log('ERROR : ',json.error);
             }
                
         }
          else if(http.status != 200){
              
          }
        }
     http.send(formData);
    
   }