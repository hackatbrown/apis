
$(document).ready(function() {
	var APIs = [
		{
			name: "Dining",
			endpoints: [
				{
					endpoint: "/dining/menu",
					required: ['eatery'],
					optional: ['year', 'month', 'day', 'hour', 'minute'],
					placeholders: { year: 'current', month: 'current', day: 'current', hour: 'current', minute: 'current' },
					options: {eatery: ['ratty', 'vdub']},
					defaults: {eatery: 'ratty'}
				}
			]
		}
	]
	
	var Console = React.createClass({
		getInitialState: function() {
			return {
				"visible": true,
				"api": "Dining",
				"endpoint": "/dining/menu",
				"params": {"eatery": "ratty"}
			}
		},
		getAPINamed: function(name) {
			var self = this;
			for (var i=0; i<this.props.apis.length; i++) {
				var api = this.props.apis[i];
				if (api.name == name) {
					return api;
				}
			}
		},
		getEndpointNamed: function(api, name) {
			var self = this;
			for (var i=0; i<api.endpoints.length; i++) {
				var endpoint = api.endpoints[i];
				if (endpoint.endpoint == name) {
					return endpoint;
				}
			}
		},
		render: function() {
			var self = this;
			var topRowContent = null;
			var expansion = null;
			if (self.state.visible) {
				topRowContent = [
					self.renderAPIPicker(),
					<div key='hide' className='showhide' onClick={() => { self.setState({visible: false})}}>Hide console</div>
				]
				expansion = [<h1>Hello, world</h1>]
			} else {
				topRowContent = [<div key='show' className='showhide' onClick={() => { self.setState({visible: true}) }}>Try it</div> ]
			}
			return (
				<div>
					<div className='top-row'>{topRowContent}</div>
					<div className='expansion'>{expansion}</div>
				</div>
			)
		},
		renderAPIPicker: function() {
			var self = this;
			var options = self.props.apis.map((api) => { return <option value={api.name}>{api.name}</option> });
			console.log(options)
			var change = function(e) {
				var api = e.target.value;
				if (api != self.state.api) {
					self.setState({api: api, endpoint: self.getAPINamed(api).endpoints[0].endpoint});
				}
			}
			return <select key='api-picker' onChange={change} defaultValue={self.state.api}> {options} </select>;
			
		}
	})
	ReactDOM.render(<Console apis={APIs}/>, document.getElementById('console'));	
})
