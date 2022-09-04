// fetch = require('node-fetch');
// import pdf2base64 from '../pdf-to-base64';

async function send_whatsapp_js(wapp, msg) {
    const response = await fetch('http://168.197.50.133/sendText', {
        method: 'POST',
        headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
        body: JSON.stringify(
                    {
                        sessionName: "romitex", 
                        number: wapp,
                        text:msg,
                    }
                )
              });
        const content = await response.json();
            
        console.log(content);
    }
// send_whatsapp_js('5493512368562','sigo hinchando las bolas')



async function send_file_js(wapp, file){
    const pdf = await pdf2base64(file)
    const response = await fetch('http://168.197.50.133/sendFile', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(
        {
            sessionName: "romitex", 
            number: wapp,
            base64Data: pdf, //hexadecimal
            fileName:file,
            caption: "" //optional
        }
    )
  });
  const content = await response.json();
  console.log(content);
}
// send_file_js('5493512368562', 'intimacion.pdf')
