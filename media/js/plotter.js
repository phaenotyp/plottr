/*
example_query = {
   country : 'de',
   zip : '53111',
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
         infobar_msg : '#infobar',
         eventhook : '#head'   // this is the node that takes the custom events.
      },
      // mappping to classes in css files
      // not sure if this is necessary. let's see.
      css : {


      },
      // events, define bindings via jquery
      events : {
         // fires when dates finished loading via ajax.
         onDatesLoad : 'onDatesLoad',
         // fires when the ajax call to get Dates is made.
         beforeDatesLoad : 'beforeDatesLoad',
         //
         onDatesUpdated : 'onDatesUpdated'
      },
      // misc
      // default values for querying dates from the server.
      default_query : {
         date : 'today', country : 'de'
      },
      query_validation : {
         // query validation contains functions to validate members of a query object.
         // every function validates the member of a query with the same name.
         // all members are optional.
         // if there shold be required members, a proptery of the validation function, would be a good idea. (_validate_query would have to be modified.)
         date : function(subject){
            // this validates the date part of a query. 
            var literals = ['today', 'tomorrow'];
            var regex = '\\d{4}(-\\d{1,2})?(-\\d{1,2})?';
            if ($.inArray(subject, literals)!=-1) return true;  
            if (new RegExp(regex).test(subject)) return true;
            return false;
         },
         country : function(subject){
            // this validates the country part of a query
            if(subject != 'de') return false;
            return true;
         },
         zip : function(subject){
            return (new RegExp('^\\d{1,5}$').test(subject)); 
         }  
         

      },
      url_template : '/dates/{{ date }}/',
      date_template : '',
      jquery_ajax_defaults : {
         dataType: 'json',
         type: 'GET',
         error : function (xhr, status, error) {
           // if there was an error in the ajax request, display it.
           PLTR.infobar.error('Ajax-Error! ' + this.url + ' ' + error);
         }
      }
   }, // end of conf
   // functions and variables that deal with the dates themselves
   dates : {
     _validate_query : function(query){
        // validates a query object using the function in PLTR.conf.query_validation

        // walk through all methods of query_validation
        // and validate a same named member of the query with them.
        for( attr in PLTR.conf.query_validation ){
           if( $.isFunction( PLTR.conf.query_validation[attr] ) && query[attr]){
              // this should call the method attr of query_validation and pass it the member of query by the same same
              if(!PLTR.conf.query_validation[attr](query[attr])) return false;
           }
        }
        return true;
     },
     _query_url : function(query){
        // takes a query-object and returns a url to get matching dates from the server.
        var url = '/dates/';
        if(query.date) url += query.date + '/';
        if(query.country){
           url += query.country;
           if(query.zip){
             url += '-' + query.zip;
           }
           url += '/';
        }
        return url;
     },
     db : new TAFFY([]), // the db that contains the local copy of the dates.
     load : function(query, callback){
        // gets a list of dates from the server and fires onDatesLoad event.
        query = jQuery.extend(new PLTR.clone(PLTR.conf.default_query), query); // provide default values.
        if( PLTR.dates._validate_query(query) ){ // validate the query
           var url = PLTR.dates._query_url(query);
           $(PLTR.conf.selectors.eventhook).trigger(PLTR.conf.events.beforeDatesLoad); // trigger event.
           // make an xhr to get dates as json
           $.ajax({
              url: url,
              success : function( json ){
                 // fill PLTR.dates.db with
                 // TODO
                 // trigger an event
                 $(PLTR.conf.selectors.eventhook).trigger(PLTR.conf.events.onDatesLoad);
              }
           });
        } else { // query object was invalid.
           PLTR.infobar.error('Couldn\'t load Dates. Query Object invalid.');
        }

     },
     reload : function( datelist, callback ){  // is reload a keyword?
       // get the listed dates from the server and updates the taffydb.
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
       },
       throb : function(){
          // displays a notification that the app is busy.
       },
       stopthrob : function(){
          // removes the notification that the app is busy.
       },
       
   },
   template : {
     // template is a tiny template-engine to simplify output in js.
     // if this would support more of djangos template-engine it would
     // be possuble to get django-templates with ajax and render them in
     // the browser.  -> d.r.y.
      render : function(template, context){
          // render takes a template string and a context object.
          // every occurence of a substing like {{ key }} will be replaced
          // by context[key]
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
   },
   // makes a copy of an object
   // usage:
   // var newob = new PLTR.clone(oldob);
   clone : function (obj){
      for (attr in obj) {
         if (typeof obj[attr] == 'object') {
            // recurively clones objects // is this circle-refrence-save?
            this[attr] = new cloneObject(obj[attr]); 
         } else this[attr] = obj[attr];
      }
   },
   // initialises Plotter.
   init : function(){
      jQuery.ajaxSetup(PLTR.conf.jquery_ajax_defaults);

      // bind events
      $(PLTR.conf.selectors.eventhook).bind(PLTR.conf.events.onDatesLoad, PLTR.dates.render);

   }
};  // end of PLTR;