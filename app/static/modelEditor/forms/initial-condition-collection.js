var $ = require('jquery');
var AmpersandView = require('ampersand-view');
var AmpersandFormView = require('ampersand-form-view');
var InputView = require('ampersand-input-view');
var SelectView = require('ampersand-select-view');
var InitialConditionFormView = require('./initial-condition');
var PaginatedCollectionView = require('./paginated-collection-view');

var Tests = require('./tests');
var AddNewInitialConditionForm = AmpersandFormView.extend({
    submitCallback: function (obj) {
        if(obj.type == 'scatter')
        {
            var model = this.collection.addScatterInitialCondition(this.baseModel.species.at(0), 0, this.baseModel.mesh.uniqueSubdomains.at(0));
        }
        else if(obj.type == 'place')
        {
            var model = this.collection.addPlaceInitialCondition(this.baseModel.species.at(0), 0, 0, 0, 0);
        }
        else if(obj.type == 'distribute')
        {
            var model = this.collection.addDistributeUniformlyInitialCondition(this.baseModel.species.at(0), 0, this.baseModel.mesh.uniqueSubdomains.at(0));
        }
    },
    initialize: function(attr, options) {
        this.collection = options.collection;

        this.selectView = attr.selectView;
        this.baseModel = this.collection.parent;

        this.fields = [
            new SelectView({
                label: 'Type: ',
                name: 'type',
                value: 'scatter',
                options: [['scatter', 'Scatter'], ['place', 'Place'], ['distribute', 'Distribute Uniformly']],
                required: true,
            })
        ];

    },
    render: function()
    {
        AmpersandFormView.prototype.render.apply(this, arguments);

        this.button = $('<button class="btn btn-primary" type="submit">Add Initial Condition</button>').appendTo( $( this.el ) );
    }
});

var InitialConditionCollectionFormView = AmpersandView.extend({
    template : "<div>\
  <div data-hook='initialConditionCollection'></div> \
  <h4>Add Initial Condition</h4>\
  <form data-hook='addInitialConditionForm'></form>\
</div>",
    render: function()
    {
        this.baseModel = this.collection.parent;

        var collectionTemplate = "<div> \
  <table data-hook='table'>\
    <thead>\
      <th></th><th>Type</th><th>Specie</th><th>Details</th>\
    </thead>\
    <tbody data-hook='items'> \
    </tbody> \
  </table>\
  <div data-hook='nav'> \
    <button class='btn' data-hook='previous'>&lt;&lt;</button> \
    [ <span data-hook='position'></span> / <span data-hook='total'></span> ] \
    <button class='btn' data-hook='next'>&gt;&gt;</button> \
  </div> \
</div>";

        AmpersandView.prototype.render.apply(this, arguments);

        this.selectView = this.renderSubview( new PaginatedCollectionView( {
            template : collectionTemplate,
            collection : this.collection,
            viewModel : InitialConditionFormView,
            limit : 10
        }), this.queryByHook('initialConditionCollection'));

        this.addForm = new AddNewInitialConditionForm(
            { 
                el : this.el.querySelector('[data-hook=addInitialConditionForm]'),
                selectView : this.selectView
            },
            {
                collection : this.collection
            }
        );

        //this.addForm.render();

        return this;
    }
});

module.exports = InitialConditionCollectionFormView