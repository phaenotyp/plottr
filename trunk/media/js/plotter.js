/*
example_query = {
   place : 'de-53111',
   date : '2008-11-21',
   categories : ['party', 'concert', 'sport'],
}
*/

// one root object not to pollute the namespace 
var PLTR = {
   log :  console.log || window.alert,
   conf : {
      // jquery css selectors for the elements of the app 
      selectors : {
         content : '#content',
         main : '#primary',
         sidebar : '#secondary',
         infobar_container : '#infobar',
         infobar_msg : '#infobar'
      }, 
      // mappping to classes in css files 
      // not sure if this is necessary. let's see. 
      css : { 
         

      }, 
      // events, define bindings via jquery
      events : {
         // fires when dates finished loading via ajax.
         onDatesLoad : 'onDatesLoad',
     
         //
         onDatesUpdated : 'onDatesUpdated'
      },
      // misc
      default_query : {
         date : 'today' 
      },
      url_template : '/dates/{{ date }}/', 
      date_template : ''
   },

   // functions and variables that deal with the dates themselves 
   dates : {
     db : new TAFFY([]),
     load : function(query, callback){
       // gets a list of dates from the server and fires onDatesLoad event.

       
     },
     reload : function( datelist, callback ){
       // get the listes dates from the server and
     },
     render : function( dateid ){
       // gets a date from taffydb and returns a domnode/html-represention.
       // should this somehow be templated?
     },
   },
   // behaviour of the sidebar 
   sidebar : {
      hide : function(){
      },
      show : function(){
      }
   },
   // infobar gives status reports of the application to the user. like 'saved successfuly', 'loading' or 'connection lost'  
   // could also be used to broadcast to all clients from the server.
   infobar : {
       message : function(msg){ 
          // displays an info-message  
          $(PLTR.conf.selectors.infobar_msg).text(msg)
          $(PLTR.conf.selectors.infobar_container).show();
       },
       error : function(msg){
          // displays an error-message   
          $(PLTR.conf.selectors.infobar).text(msg)..show();
       },  
       poll_server : function(msg){
          // checks server for messages and displays them  
       }  
   },
   template : {
       render : function(template, context){
          var text = template; 
          for (var key in context){
             text = text.replace( 
                       new RegExp( "\\{\\{ " + key + " \\}\\}", "gi" ), 
                       context[key]
             ); 
          } 
          return text; 
       } 
   },  
   map : {
      hide : function(){
      },
      show : function(){
      },
      load_dates : function(){
      },
      zoom_to : function( dateid ){
      }
   }
}
