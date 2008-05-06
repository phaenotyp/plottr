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
                      
         // this is the element that hold the dates. 
         dates_container : 'ul#dates',   
         dates : 'ul#dates>li',   
          
         // the navigation bar   
         queryeditor : 'div#navi', 

         // the items of the navigation in the header 
         header_navi : 'ul#headnavi>li',
         // the containers of the navigation elements in the header
         header_navi_items : '.headnavi_items',
         // the infobar displays messages to the user
         infobar_container : '#infobar',
         infobar_msg : '#infobar',  // the messages are in the innerHtml of this
         eventhook : '#header',   // this is the node that takes the custom events.
         navi : {
            // selectors for the query-editor, code that uses this 
            // is found in PLTR.navi 
            
            date_display : '#navi_date_display',
            country_display : '#navi_country_display',
            zips_display : '#navi_zips_display',
            

            // *_widget are the boxes that are displayed to allow changing 
            date_widget : '#navi_date',
            zips_widget : '#navi_zips',
            country_widget : '#navi_country',
         },
      },
      // mappping to classes in css files
      // not sure if this is necessary. let's see.
      css : {
          // to keep design an layout separated and still provide fallback 
          // the classname dynamic is used to introduce layout changes with
          // javascript
          dynamic : 'dynamic',
          attention : 'attention', 

      },
      // events, define bindings via jquery
      events : {
         // fires when dates finished loading via ajax.
         onDatesLoad : 'onDatesLoad',
         // fires when the ajax call to get Dates is made.
         beforeDatesLoad : 'beforeDatesLoad',
         //
         onDatesUpdated : 'onDatesUpdated',
         // fires when the query-editor was used to change the query
         onQueryChanged : 'onQueryChanged',
         // fires when the ziplist of the query editor was altered
         // comes before onQueryChanged.
         onZiplistChanged : 'onZiplistChanged',
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
         // if there shold be required members, a proptery of the validation function, would be a good idea.
         // (_validate_query would have to be modified.)
         date : function(subject){
            // this validates the date part of a query. 
            var literals = ['all', 'today', 'tomorrow'];
            var regex = '\\d{4}(-\\d{1,2})?(-\\d{1,2})?$';
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
            // so far only german zip-code (postleitzahlen) are valid.
            // either a list of zip or a single posibly partial zip are 
            // valid
            if( PLTR.isArray(subject)){
               if(subject.length == 0) return false; 
               for(var i=subject.length-1; i>=0; i-- ){
                  if( !new RegExp('^\\d{1,5}$').test(subject[i]) ){ 
                     return false; 
                  }
               }
               return true;
            } else {
               // the system is supposed to treat too short zip-codes
               // as if there was a trailing wildcard. 
               return (new RegExp('^\\d{1,5}$').test(subject)); 
            }
         }  
      },
      _date_template : '<li><a href="{{ absolute_url }}">{{ summary }}</a> - {{ startdate }}</li>',
      date_template : '<li class="vevent" id="date_{{ id }}">\
    <div class="dtstart" title="{{ startmicroformat }}">\
       <span class="month">{{ startmonth }}</span>\
       <span class="day">{{ startday }}</span>\
       <span class="year">{{ startyear }}</span>\
    </div>\
    <div>\
      <a class="location">{{ location }}<a/>\
      <a class="summary url" href="{{ absolute_url }}">{{ summary }}</a>\
    </div>\
    <span class="clear"></span>\
  </li>',
      box_template:'<div class="box"><h2>{{ title }}</h2><div>{{ text }}</div></div>',
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
        // TODO should be able to take a date-object as date
        if(!this._validate_query(query)){ return false };
        // provide default values.
        query = jQuery.extend(new PLTR.clone(PLTR.conf.default_query), query); 
        // build the url 
        var url = '/dates/';
        if(query.date) url += query.date + '/'; // date
        if(query.country){                     // country
           url += query.country + '/';
           if(query.zips){                 // zip is only possible with country 
              if(query.zips.join){
                 url += query.zips.join(',');  // a list of zips
              } else {
                 url += querys.zip; /// a single or partial zip
              }
              url += '/';
           }
        }
        return url;
     },
     db : new TAFFY([]), // the db that contains the local copy of the dates.
     load : function(query, callback){
        // gets a list of dates from the server and fires onDatesLoad event.
        if( PLTR.dates._validate_query(query) ){ // validate the query
           var url = PLTR.dates._query_url(query);
           PLTR.events.trigger('beforeDatesLoad'); // trigger event.
           // make an xhr to get dates as json
           $.ajax({
              url: url,
              success : function( json ){
                 PLTR.dates.db = new TAFFY([])
                 // fill PLTR.dates.db with
                 $.each(json, function(index, value){ 
                    PLTR.dates.db.insert(value); 
                 });
                 // trigger an event
                 PLTR.events.trigger('onDatesLoad');
              }
           });
        } else { // query object was invalid.
           PLTR.infobar.error('Couldn\'t load Dates. Query Object invalid.');
           PLTR.log('An invalid Query was passed to PLTR.dates.load'); 
           PLTR.log(query); 
        }

     },
     details : function( dateob, target ){
        // displays the detail-information of one date.
        target = target || PLTR.conf.selectors.sidebar;
        details = ''; 
        /* location */
        var title = dateob.locationdata ? dateob.locationdata.name : 'Adresse';
        var text = dateob.adressdata.street + '<br />';
        text += dateob.adressdata.zipcode + ', ' + dateob.adressdata.city;
        details += PLTR.template.render(PLTR.conf.box_template, {
             title : title, 
             text : text }); 
      
 
        /* a box for the description */
        if( dateob.description )
            details += PLTR.template.render(PLTR.conf.box_template, {
             title : 'Description', 
             text : dateob.description, }); 
        // append everything
        $(target).empty().append(details); 
     }, 
     reload : function( datelist, callback ){  // is reload a keyword?
       // get the listed dates from the server and updates the taffydb.
     },
     renderone : function(datex, target ){
        // renders one date (json) with the template in
        // PLTR.conf.date_template and appends it to target 
        // if target is not given the selector 'dates_containter'
        // is used instead
        target = target || PLTR.conf.selectors.dates_container;
        var dateext = { 
           startmicroformat : '2008-04-09T08:00:00',
           startmonth : 'April',
           startday : '19',
           startyear : '2008', 
           location : (datex.locationdata ? datex.locationdata.name : datex.adressdata.street),
        }; 
        datex = jQuery.extend(datex, dateext); 
        // build the url 
        var rendered = PLTR.template.render(PLTR.conf.date_template, datex); 
        $(target).append(rendered); 
        return rendered;
     },  
     render : function(obj, target){
       // TODO better description of function
       // this goes through the passed list 
       // and calls renderone for each element
       target = target || PLTR.conf.selectors.dates_container;
       obj = obj || PLTR.dates.db.get(); 
       $(target).empty(); 
       for(var i=0, max=obj.length; i<max; i++){
          PLTR.dates.renderone(obj[i], target);
       }
       $(PLTR.conf.selectors.dates+':odd').addClass('odd'); 
       $(PLTR.conf.selectors.dates).click(PLTR.dates._list_click); 
          
     },
     _list_click : function(e){
        $(PLTR.conf.selectors.dates).removeClass('selected');
        $(this).addClass('selected'); 
        var id = $(this).attr('id').split('_')[1]; 
        PLTR.log( 'Show details for id ' + id  ); 
        PLTR.dates.details(PLTR.dates.db.first({'id':id}));
 

     }, 
     init : function(){
        $(PLTR.conf.selectors.dates).click(PLTR.dates._list_click); 
            
     }, 
   },
   header : { 
    // behaviour of the header. mainly the navigation in the header.
    init : function(){ 
       // hide the content of the header navi   
       // TODO: should be changed to use class dynamic in css
      // $(PLTR.conf.selectors.header_navi_items)
      //   .hide();
       
       // show single items on mouse-over
       $(PLTR.conf.selectors.header_navi).bind('mouseenter', function(){
           $(PLTR.conf.selectors.header_navi_items).hide();
           $(this).find(PLTR.conf.selectors.header_navi_items).show();
       });
       
    } 
   },
   navi : {
    // the navigation-bar or 'query-editor' 
    query_items : ['date','country','zips'], 
    zips : [ 53111, 50667 ],
    init : function(){
      // add methods to the ziplist.
      // the idea here is to provide a nicer and save interface for 
      // interacting with the list. also a change-event is released 
      // to make it possible to act on that. later the function 
      // to redisplay the list is bound on this event
      PLTR.navi.zips.remove = function(zip){ 
        // removes a zip from the ziplist
        var index = this.indexOf(parseInt(zip));
        this.splice(index,1);
        PLTR.events.trigger('onZiplistChanged');
      };

      PLTR.navi.zips.change = function(oldzip, newzip){
         // changes a zip without changing the index in the array
         var index = this.indexOf(parseInt(oldzip));
         newzip = parseInt(newzip); 
         // check if the new index is not alleady in the array
         if(this.indexOf(newzip)==-1 ){ 
            this[index] = newzip; 
         } else {
            // if the new value isn't unique, the old zip is dropped.
            this.splice(index,1);
         }
         PLTR.events.trigger('onZiplistChanged');
      };

      PLTR.navi.zips.append = function(zip){
         // adds a zip only if it's unique.
         zip = parseInt(zip); 
         if(this.indexOf(zip)==-1){ 
            //this.push(zip); 
            this[this.length] = zip; 
            PLTR.events.trigger('onZiplistChanged');
         }
      };

      // if the ziplist was changed, it should be automaticly redisplayed.
      PLTR.events.bind('onZiplistChanged', PLTR.navi.display_zips); 

      PLTR.events.bind('onQueryChanged', function(){ 
          PLTR.log('The Query was changed');
          PLTR.dates.load(PLTR.navi.get_query()); 
      }); 

      // bind the onlick event for the date-widget
      $(PLTR.conf.selectors.navi.date_display)
          .click(PLTR.navi.display_date_widget);
      
      PLTR.navi.display_zips();        
      // bind the event for the zips-widget
      $(PLTR.conf.selectors.navi.zips_display).click(PLTR.navi._ziplist_click); 
 
      // hook onclick events to the display elements of the qed
      /*
      for(var i=0, max=PLTR.navi.query_items.length; i<max; i++){
          var item = PLTR.navi.query_items[i];
          var displayfunc = 'display_'+item+'_widget';
          if(PLTR.navi[displayfunc]){ 
             $(PLTR.conf.selectors.navi[item+'_display'])
                .click(PLTR.navi[displayfunc]);
          }
      }
      */
    },
    get_query : function(){ 
       // returns a query object based on the current selection 
       // in the query editor.
       var query = {}; 
       query.date = $(PLTR.conf.selectors.navi.date_display).html();
       query.country = 'de';
       query.zips = PLTR.navi.zips;
       return query; 
    }, 
    display_date_widget : function(){
        $(PLTR.conf.selectors.navi.date_widget)
           .css('position','absolute') 
           .css('z-index',1000) 
           .show() 
           .click(function(e){
              if(e.target.title){ /* if the clicked element has a title-attr 
                 it is assigned to the displaying element   */ 
                 $(PLTR.conf.selectors.navi.date_display).html(e.target.title);
                 /* the closing of the widget is done by one-time click event
 *                assigned lower. */
                 PLTR.events.trigger('onQueryChanged');
              } else { 
                 /* prevent further propagation, thus no closing */
                 return false; 
              }
           })
           .find('input')  // deal with the input for dates  
           .removeClass(PLTR.conf.css.attention) 
           .keypress( function(e){
             if(e.keyCode==27){ $('body').trigger('click');  } // esc
             else if(e.keyCode==13){  // if return is pressed...
               var val =  $(this)[0].value; // get the input..
               if( PLTR.conf.query_validation.date(val)){ // validate..
                   $(PLTR.conf.selectors.navi.date_display) 
                       .html(val);  // assign 
                   $('body').trigger('click'); //close widget  
                   PLTR.events.trigger('onQueryChanged');
                } else { 
                   $(this).addClass(PLTR.conf.css.attention); 
                }
             }; 
           })[0].focus(); 
        $('body').one('click', function(){
           $(PLTR.conf.selectors.navi.date_widget).hide(); 
        });
        return false; // stop further propagation
    },
    display_zips : function(){
       // takes the ziplist in PLTR.navi.zips and displays it 
       // in the Query Editors interface 
       // should maybe use a template to be flexible.
       var max = PLTR.navi.zips.length;
       $(PLTR.conf.selectors.navi.zips_display).empty();
       $.each(PLTR.navi.zips, function(index, zip){
         var zip = '<span class="zip" title="'+zip+'">'+zip+'</span>';
         if(max>1) zip += '<span class="removezip"> [-]</span>';
         $(PLTR.conf.selectors.navi.zips_display).append('<li>'+zip+'</li>');
       });
       $(PLTR.conf.selectors.navi.zips_display)
          .append('<li><span id="addzip">[+]</span></li>');
       PLTR.events.trigger('onQueryChanged');
    }, 
    display_country_widget : function(){
    },
    _ziplist_click : function(e){ 
       // handles a click on the ziplist, supposed to be an eventhandler
       // does event-delegation
       // in case a [-] button was clicked
       if(e.target.className.indexOf('removezip')!=-1){
         // remove the corresponding zip from PLTR.navi.zips
         var zip = $(e.target.parentNode).find('span.zip').attr('title');
         PLTR.navi.zips.remove(zip); 
       } else if(e.target.className.indexOf('zip')!=-1){ 
         // one zip was clicked to be changed
         var target = e.target;
         var oldzip = $(target).attr('title'); 
         // the keypress event-handler is assigned to a variable. 
         // this is because it uses the variables target and oldzip
         // in a closure. closure-variables are set at the definition of 
         // the function, unless the function is redefined explicitly 
         // the values for target and oldzip from the time of the first call
         // to keypress are taken.  
         var keypress = function(e){
               if(e.keyCode==27){ // escape
                  $(target).html(oldzip); // write back the old val
               } else if(e.keyCode==13){ //return
                  // change PLTR.navi.zips
                  PLTR.navi.zips.change(oldzip, $(this).find('input').val());
               }   
           };
         $(e.target)
           // exchange the zip with an input field 
           .html($('<input>').val(oldzip).attr({maxlength:5, size:5}))
           // assign keypress events to it
           .keypress(keypress).find('input')[0].focus();
         // assing a one time click event to body, closing the 
         // input field. 
         $('body').one('click', function(){ 
            $(target).html(oldzip);
         });
         return false; // stop further propagation, stops the one-time event 
  
       } else if(e.target.id=='addzip'){ // add button was clicked
         // here a closure is used again but no need to reassign since
         // the value of e.target doesn't change in this chase 
         var target = e.target;
         $(e.target)
           // excange the [+] with an input field
           .html($('<input>').attr({maxlength:5, size:5}))
           .keypress(function(e){
               if(e.keyCode==27){ // escape
                  $(target).html('[+]'); // write back the old val
               } else if(e.keyCode==13){ //return
                  // change PLTR.navi.zips
                  PLTR.navi.zips.append($(this).find('input').val()); 
               }   
           })
           .find('input')[0].focus();
         $('body').one('click', function(){ 
           $(target).html('[+]');
         });
         return false; // stop further propagation, stops the one-time event 
       }
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
       init : function(){
          $(PLTR.conf.selectors.infobar_container).click(function(){
             PLTR.infobar.clear();
          });
       }, 
       message : function(msg){
          // displays an info-message
          this.clear();
          $(PLTR.conf.selectors.infobar_msg).text(msg)
          $(PLTR.conf.selectors.infobar_container).addClass('message').show();
       },
       error : function(msg){
          // displays an error-message
          this.clear();
          $(PLTR.conf.selectors.infobar_msg).text(msg);
          $(PLTR.conf.selectors.infobar_container).addClass('error').show();
       },
       warning : function(msg){
          // displays an error-message
          this.clear();
          $(PLTR.conf.selectors.infobar_msg).text(msg);
          $(PLTR.conf.selectors.infobar_container).addClass('warning').show();
       },
       clear : function(){
          // displays an error-message
          $(PLTR.conf.selectors.infobar_msg).empty();
          $(PLTR.conf.selectors.infobar_container)
             .removeClass('warning')
             .removeClass('error')
             .removeClass('message');
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
   // from the future: 
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
   events : {
   // events tries to simplify the usage of the event system in plotter. 
   // to invoke a custom event do 
   // PLTR.events.trigger('eventname');
   // note that eventname has to be listed in PLTR.conf.events 
   // to bind a listener to a plotter-event do
   // PLTR.events.bind('eventname', function(){ dostuff(); }); 
      _get : function(e){ 
         // this function takes a name of an event and returns the event-string
         // makes it possible to call
         // PLTR.events.trigger('onDatesLoad');  instead of
         // PLTR.events.trigger(PLTR.conf.events.onDatesLoad); 
         for (attr in PLTR.conf.events){
             if(attr == e) return PLTR.conf.events[attr]; 
             if(PLTR.conf.events[attr] == e) return e; 
         } 
         PLTR.infobar.warning('No Event ' + e + ' defined.' );  
         return e;
      },
      bind : function( e, f ){
         // bind a function to an event 
        $(PLTR.conf.selectors.eventhook).bind(PLTR.events._get(e),f);
      }, 
      trigger : function( e ){
         // triggers an event 
         $(PLTR.conf.selectors.eventhook).trigger(PLTR.events._get(e));
      }, 
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
   isArray : function(obj){
       // returns true if the passed object is an array
       return (obj.constructor.toString().indexOf("Array") != -1); 
   },
   // initialises Plotter.
   init : function(){

      // body gets the class dynamic.
      // all css-changes for stepwise enhancement of the site 
      // should be hooked to that class.
      $('body').addClass(PLTR.conf.css.dynamic);

      // call individual init functions.
      // iterating over the subsections of PLTR and call any init() 
      // in the first-child-level
      // so all functions 'init' of direct object-members of PLTR will be
      // called.
      for( section in PLTR){
         if(  typeof(PLTR[section])=='object'){
            if( PLTR[section].init  && $.isFunction(PLTR[section].init)){ 
               PLTR[section].init(); 
            }
         }
      }

      // assign sesible defaults to all ajax-calls.
      jQuery.ajaxSetup(PLTR.conf.jquery_ajax_defaults);

      // bind events
      PLTR.events.bind('onDatesLoad', function(){ PLTR.dates.render(); });
      PLTR.events.bind('onDatesLoad', function(){ PLTR.log('New Dates have been loaded.');});

   }
};  // end of PLTR;


$(PLTR.init); 
