# ATLAS Palantir Foundry Development Guide

This repository contains code for the ATLAS project that runs in Palantir Foundry. It provides rules, templates, and examples for developing code that seamlessly transitions from local development to the Palantir Foundry environment.

## Development Workflow

1. **Local Development**: Code is developed on Mac OS
2. **Version Control**: Code is synced to GitHub
3. **Deployment**: Code is deployed to Palantir Foundry

## Key Files

- **[FOUNDRY_DEVELOPMENT_RULES.md](./FOUNDRY_DEVELOPMENT_RULES.md)**: Essential rules for Foundry-compatible code
- **[foundry_template.py](./foundry_template.py)**: Template Python file with best practices
- **[template_function.yml](./template_function.yml)**: Template YAML configuration for Foundry functions

## Getting Started

1. Clone this repository
2. Review the development rules in `FOUNDRY_DEVELOPMENT_RULES.md`
3. Use the templates as a starting point for new functions
4. Install dependencies: `pip install -r requirements.txt`
5. Test locally before deploying to Foundry

## Local Testing

The template includes a `main()` function that allows for local testing:

```bash
python foundry_template.py
```

This simulates the Foundry environment by creating a local Spark session and sample data.

## Creating New Functions

1. Copy `foundry_template.py` and rename it for your specific function
2. Copy `template_function.yml` and update it with your function's details
3. Implement your business logic in the main function
4. Test locally
5. Deploy to Foundry

## Security Notes

- Never commit secrets or credentials to the repository
- Use environment variables for local testing
- Use Foundry's secret management for production

## Common Issues and Resolutions

- **Memory Errors**: Adjust the memory allocation in the function YAML
- **Timeout Errors**: Increase the timeout setting or optimize your code
- **Dependency Issues**: Ensure all dependencies are specified with exact versions
- **Spark vs. Pandas**: Use Spark operations for large datasets, Pandas for smaller ones

## Additional Resources

- Review existing code in this repository for real-world examples
- See `function.yml` and `appointment_pipeline.yml` for production configuration examples

## Contributing

1. Create a feature branch (`git checkout -b feature/your-feature`)
2. Make your changes following the Foundry development rules
3. Test thoroughly locally
4. Submit a pull request 